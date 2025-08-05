const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const path = require('path');
const fs = require('fs');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// Middleware
app.use(express.json());
app.use(express.static('.'));

// Store latest data
let latestData = {
    clf_data: null,
    mc_data: null,
    feedback_status: null
};

// WebSocket clients
const clients = new Set();

// WebSocket connection handler
wss.on('connection', (ws) => {
    console.log('New WebSocket client connected');
    clients.add(ws);
    
    // Send current data to new client
    if (latestData.clf_data) {
        ws.send(JSON.stringify({
            type: 'clf_data',
            value: latestData.clf_data.value,
            timestamp: latestData.clf_data.timestamp
        }));
    }
    
    if (latestData.mc_data) {
        ws.send(JSON.stringify({
            type: 'mc_data',
            params: latestData.mc_data.params,
            timestamp: latestData.mc_data.timestamp
        }));
    }
    
    if (latestData.feedback_status) {
        ws.send(JSON.stringify({
            type: 'feedback_status',
            sent: latestData.feedback_status.sent,
            timestamp: latestData.feedback_status.timestamp
        }));
    }
    
    ws.on('close', () => {
        console.log('WebSocket client disconnected');
        clients.delete(ws);
    });
    
    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
        clients.delete(ws);
    });
});

// Broadcast to all connected WebSocket clients
function broadcast(data) {
    const message = JSON.stringify(data);
    clients.forEach(client => {
        if (client.readyState === WebSocket.OPEN) {
            client.send(message);
        }
    });
}

// POST endpoint for classifier data
app.post('/clf_data', (req, res) => {
    try {
        const { value, rep } = req.body;
        
        if (value === undefined || rep === undefined) {
            return res.status(400).json({ error: 'Missing required fields: value, rep' });
        }
        
        console.log(`Received classifier data - Rep: ${rep}, Value: ${value}`);
        
        // Store latest data
        latestData.clf_data = {
            value: parseFloat(value),
            rep: parseInt(rep),
            timestamp: new Date().toISOString()
        };
        
        // Broadcast to WebSocket clients
        broadcast({
            type: 'clf_data',
            value: latestData.clf_data.value,
            rep: latestData.clf_data.rep,
            timestamp: latestData.clf_data.timestamp
        });
        
        res.json({ success: true, message: 'Classifier data received' });
        
    } catch (error) {
        console.error('Error processing classifier data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// POST endpoint for motion correction data
app.post('/mc_data', (req, res) => {
    try {
        const { params, rep } = req.body;
        
        if (!params || !Array.isArray(params) || rep === undefined) {
            return res.status(400).json({ error: 'Missing required fields: params (array), rep' });
        }
        
        console.log(`Received motion correction data - Rep: ${rep}, Params: [${params.join(', ')}]`);
        
        // Store latest data
        latestData.mc_data = {
            params: params.map(p => parseFloat(p)),
            rep: parseInt(rep),
            timestamp: new Date().toISOString()
        };
        
        // Broadcast to WebSocket clients
        broadcast({
            type: 'mc_data',
            params: latestData.mc_data.params,
            rep: latestData.mc_data.rep,
            timestamp: latestData.mc_data.timestamp
        });
        
        res.json({ success: true, message: 'Motion correction data received' });
        
    } catch (error) {
        console.error('Error processing motion correction data:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// POST endpoint for neurofeedback status
app.post('/feedback_status', (req, res) => {
    try {
        const { sent, rep } = req.body;
        
        if (sent === undefined || rep === undefined) {
            return res.status(400).json({ error: 'Missing required fields: sent (boolean), rep' });
        }
        
        console.log(`Received neurofeedback status - Rep: ${rep}, Sent: ${sent}`);
        
        // Store latest data
        latestData.feedback_status = {
            sent: Boolean(sent),
            rep: parseInt(rep),
            timestamp: new Date().toISOString()
        };
        
        // Broadcast to WebSocket clients
        broadcast({
            type: 'feedback_status',
            sent: latestData.feedback_status.sent,
            rep: latestData.feedback_status.rep,
            timestamp: latestData.feedback_status.timestamp
        });
        
        res.json({ success: true, message: 'Neurofeedback status received' });
        
    } catch (error) {
        console.error('Error processing neurofeedback status:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// GET endpoint for latest data (fallback for polling)
app.get('/api/latest-data', (req, res) => {
    res.json(latestData);
});

// Serve the dashboard HTML
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'dashboard.html'));
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        timestamp: new Date().toISOString(),
        connectedClients: clients.size,
        latestData: {
            clf_data: latestData.clf_data ? {
                value: latestData.clf_data.value,
                rep: latestData.clf_data.rep,
                timestamp: latestData.clf_data.timestamp
            } : null,
            mc_data: latestData.mc_data ? {
                params: latestData.mc_data.params,
                rep: latestData.mc_data.rep,
                timestamp: latestData.mc_data.timestamp
            } : null,
            feedback_status: latestData.feedback_status ? {
                sent: latestData.feedback_status.sent,
                rep: latestData.feedback_status.rep,
                timestamp: latestData.feedback_status.timestamp
            } : null
        }
    });
});

// Error handling middleware
app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).json({ error: 'Internal server error' });
});

// Start server
const PORT = process.env.PORT || 5001;

// Add error handling for the server
server.on('error', (error) => {
    console.error('Server error:', error);
    if (error.code === 'EADDRINUSE') {
        console.error(`Port ${PORT} is already in use. Please try a different port.`);
        process.exit(1);
    }
});

server.listen(PORT, () => {
    console.log(`Dashboard server running on http://localhost:${PORT}`);
    console.log(`WebSocket server ready for real-time updates`);
    console.log(`POST endpoints:`);
    console.log(`   - /clf_data (classifier output)`);
    console.log(`   - /mc_data (motion correction parameters)`);
    console.log(`   - /feedback_status (neurofeedback status)`);
    console.log(`Health check: http://localhost:${PORT}/health`);
    console.log(`Press Ctrl+C to stop the server`);
});

// Keep the process alive
process.stdin.resume();

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\nShutting down server...');
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

// Handle uncaught exceptions
process.on('uncaughtException', (error) => {
    console.error('Uncaught Exception:', error);
    server.close(() => {
        console.log('Server closed due to uncaught exception');
        process.exit(1);
    });
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('Unhandled Rejection at:', promise, 'reason:', reason);
    server.close(() => {
        console.log('Server closed due to unhandled rejection');
        process.exit(1);
    });
}); 