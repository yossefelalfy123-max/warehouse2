"""
Warehouse Management System - Main Entry Point
Supports both GUI and CLI modes
"""

import sys
import os
from datetime import datetime

def show_welcome():
    """Show welcome message"""
    print("=" * 70)
    print("🏭 WAREHOUSE MANAGEMENT SYSTEM")
    print("OOP & VVRPO Course Project - 2024")
    print("=" * 70)
    print()
    print("Select mode:")
    print("1. Graphical User Interface (GUI)")
    print("2. Command Line Interface (CLI)")
    print("3. Run Unit Tests")
    print("4. Exit")
    print()

def cli_mode():
    """Run in Command Line Interface mode"""
    print("\n📟 COMMAND LINE INTERFACE MODE")
    print("=" * 50)
    
    # Import the main module
    from warehouse_final import main as warehouse_main
    
    try:
        warehouse_main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

def gui_mode():
    """Run in Graphical User Interface mode"""
    print("\n🎨 LAUNCHING GRAPHICAL INTERFACE...")
    
    try:
        from warehouse_gui import main as gui_main
        gui_main()
    except ImportError as e:
        print(f"❌ Cannot import GUI module: {e}")
        print("Make sure warehouse_gui.py is in the same directory")
    except Exception as e:
        print(f"❌ Error starting GUI: {e}")

def test_mode():
    """Run unit tests"""
    print("\n🧪 RUNNING UNIT TESTS...")
    print("=" * 50)
    
    try:
        # Run tests from warehouse_final
        import unittest
        from warehouse_final import run_unit_tests
        
        run_unit_tests()
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")

def main():
    """Main entry point"""
    show_welcome()
    
    while True:
        try:
            choice = input("Enter choice (1-4): ").strip()
            
            if choice == "1":
                gui_mode()
                break
            elif choice == "2":
                cli_mode()
                break
            elif choice == "3":
                test_mode()
                break
            elif choice == "4":
                print("\n👋 Goodbye!")
                sys.exit(0)
            else:
                print("Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()