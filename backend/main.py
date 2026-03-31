import sys
import os
import json

# Add project root to python path to avoid ModuleNotFoundError when running as script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import process_video

def main():
    if len(sys.argv) < 2:
        print("Usage: python backend/main.py <path_to_video>")
        sys.exit(1)
        
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"Error: Video file '{video_path}' does not exist.")
        sys.exit(1)
        
    try:
        results = process_video(video_path)
        
        out_path = "output.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4)
            
        print(f"\nProcessing successful! Results saved to {out_path}")
        
    except Exception as e:
        import traceback
        print(f"\nAn error occurred during processing:\n{str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
