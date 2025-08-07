def main():
    """Main entry point for the neuroloopy CLI."""
    print("="*60)
    print("neuroloopy Real-time fMRI Processing v0.1.0")
    print("="*60)
    
    # Parse command line arguments
    args = parse_arguments()
    print(f"Arguments: {vars(args)}")
    
    # Initialize observer and handler variables for cleanup
    event_observer = None
    
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
        event_observer, event_handler = start_watcher(
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
    finally:
        # Clean shutdown
        if event_observer is not None:
            print("Stopping file observer...")
            event_observer.stop()
            event_observer.join()
            print("✓ Observer stopped")
    
    print("neuroloopy shut down successfully.")