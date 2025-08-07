#!/usr/bin/env python3
"""
Command line interface for neuroloopy real-time fMRI processing.
"""

import argparse
import sys
import time
import os
from pathlib import Path


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='neuroloopy Real-time fMRI Processing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  neuroloopy --session 2 --subjectid sub001
  neuroloopy --session 3 --debug --logging
  neuroloopy --session 2 --dashboard --config my_config

For more information, see the documentation.
        """
    )
    
    parser.add_argument('-s', '--subjectid', 
                       help='Subject ID (default: %(default)s)', 
                       default='demo')
    parser.add_argument('-sess', '--session', 
                       help='Scan session number', 
                       required=True)
    parser.add_argument('-c', '--config', 
                       help='Configuration file name (without .yaml extension) (default: %(default)s)', 
                       default='default')
    parser.add_argument('-d', '--debug', 
                       help='Enable debugging mode', 
                       action='store_true', 
                       default=False)
    parser.add_argument('-l', '--logging', 
                       help='Enable logging', 
                       action='store_true', 
                       default=False)
    parser.add_argument('-b', '--dashboard', 
                       help='Enable dashboard display', 
                       action='store_true', 
                       default=False)
    parser.add_argument('-r', '--startrun', 
                       help='Starting run number (default: %(default)s)', 
                       default='1')
    
    return parser.parse_args()


def check_config_file(config_path):
    """Check if config file exists, create template if needed."""
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        
        # Check if config directory exists
        config_dir = os.path.dirname(config_path)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print(f"Created config directory: {config_dir}")
        
        # Generate template
        from .utils import generate_config_template
        template_path = os.path.join(config_dir, "template.yaml")
        generate_config_template(template_path)
        print(f"Generated template config file: {template_path}")
        print("Please copy and customize this template for your experiment.")
        return False
    return True


def main():
    """Main entry point for the neuroloopy CLI."""
    print("="*60)
    print("neuroloopy Real-time fMRI Processing v0.1.0")
    print("="*60)
    
    # Parse command line arguments
    args = parse_arguments()
    print(f"Arguments: {vars(args)}")
    
    try:
        # Check and set up configuration
        config_path = f'config/{args.config}.yaml'
        if not check_config_file(config_path):
            sys.exit(1)
        
        print(f"\nLoading configuration from: {config_path}")
        
        # Import and set up configuration
        from .utils import setup_config
        config = setup_config(config_path, args)
        config['script_start_time'] = time.time()
        print("✓ Configuration loaded and validated")
        
        # Import the watcher module
        from .watcher import start_watcher
        print("✓ Watcher module loaded")
        
        # Start the real-time processing
        print("\n" + "="*60)
        print("STARTING REAL-TIME PROCESSING")
        print("="*60)
        print(f"Subject ID: {args.subjectid}")
        print(f"Session: {args.session}")
        print(f"Debug mode: {'ON' if args.debug else 'OFF'}")
        print(f"Logging: {'ON' if args.logging else 'OFF'}")
        print(f"Dashboard: {'ON' if args.dashboard else 'OFF'}")
        print(f"Watching directory: {config['watch_dir']}")
        print("\nPress Ctrl+C to stop")
        print("-" * 60)
        
        # Start the watcher with all configuration
        start_watcher(
            config=config,
            subject_id=args.subjectid,
            session=args.session,
            config_name=args.config,
            debug_bool=args.debug,
            logging_bool=args.logging,
            dashboard_bool=args.dashboard,
            start_run=int(args.startrun)
        )
        
        # Keep the main process alive
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal...")
            print("Shutting down neuroloopy...")
            
    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Make sure all required dependencies are installed.")
        print("Try: pip install -e .")
        sys.exit(1)
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("neuroloopy shut down successfully.")


if __name__ == '__main__':
    main()