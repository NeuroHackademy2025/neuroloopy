"""
Command line interface for neuroloopy.
"""

import argparse
import sys
import signal
import time
from pathlib import Path

from .watcher import start_watcher
from .utils import load_config, validate_config, setup_logging, create_directories


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description='Real-time fMRI neurofeedback package',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neuroloopy --config config.yaml
  neuroloopy --config config.yaml --debug
  neuroloopy --subject-id sub-01 --session 1 --run 1
        """
    )
    
    parser.add_argument(
        '--config', 
        type=str, 
        help='Configuration file path (YAML)'
    )
    parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode'
    )
    parser.add_argument(
        '--subject-id', 
        type=str, 
        help='Subject ID'
    )
    parser.add_argument(
        '--session', 
        type=int, 
        help='Session number'
    )
    parser.add_argument(
        '--run', 
        type=int, 
        help='Run number'
    )
    parser.add_argument(
        '--logging', 
        action='store_true', 
        help='Enable logging'
    )
    parser.add_argument(
        '--dashboard', 
        action='store_true', 
        help='Enable dashboard'
    )
    
    return parser


def signal_handler(signum, frame):
    """Handle interrupt signals."""
    print("\nReceived interrupt signal. Shutting down gracefully...")
    sys.exit(0)


def main():
    """Main CLI entry point."""
    # Set up signal handling
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Load configuration
    if args.config:
        if not Path(args.config).exists():
            print(f"Error: Configuration file '{args.config}' not found.")
            sys.exit(1)
        
        config = load_config(args.config)
    else:
        # Create minimal config from command line arguments
        config = {
            'subject-id': args.subject_id or 'sub-01',
            'session-number': args.session or 1,
            'start-run': args.run or 1,
            'baseline-trs': 10,
            'feedback-trs': 100,
            'moving-avg-trs': 5,
            'mc-mode': 'fsl',
            'watch-dir': './data',
            'post-url': 'http://localhost:8080',
            'archive-data': False,
            'archive-dir': './archive',
            'logging_bool': args.logging,
            'dashboard_bool': args.dashboard,
            'debug_bool': args.debug
        }
    
    # Validate configuration
    if not validate_config(config):
        print("Error: Invalid configuration.")
        sys.exit(1)
    
    # Create necessary directories
    create_directories(config)
    
    # Setup logging
    log_file, log_file_time = setup_logging(config)
    if log_file:
        config['log_file_time'] = log_file_time
    
    # Update config with CLI arguments
    config['debug_bool'] = args.debug
    config['logging_bool'] = args.logging
    config['dashboard_bool'] = args.dashboard
    
    # Extract parameters
    subject_id = config['subject-id']
    session = config['session-number']
    start_run = config['start-run']
    
    print("=" * 60)
    print("NEUROLOOPY - Real-time fMRI Neurofeedback")
    print("=" * 60)
    print(f"Subject ID: {subject_id}")
    print(f"Session: {session}")
    print(f"Start Run: {start_run}")
    print(f"Debug Mode: {args.debug}")
    print(f"Logging: {args.logging}")
    print(f"Dashboard: {args.dashboard}")
    print("=" * 60)
    
    try:
        # Start the watcher
        observer = start_watcher(
            config=config,
            subject_id=subject_id,
            session=session,
            config_name=args.config or 'command_line',
            debug_bool=args.debug,
            logging_bool=args.logging,
            dashboard_bool=args.dashboard,
            start_run=start_run
        )
        
        print("Watcher started successfully!")
        print("Press Ctrl+C to stop...")
        
        # Keep the main thread alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
        
        # Stop the observer
        observer.stop()
        observer.join()
        
        if log_file:
            log_file.close()
        
        print("Shutdown complete.")
        
    except Exception as e:
        print(f"Error: {e}")
        if log_file:
            log_file.close()
        sys.exit(1)


if __name__ == '__main__':
    main() 