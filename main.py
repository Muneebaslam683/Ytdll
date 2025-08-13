from flask import Flask, request, jsonify
import os
import yt_dlp
import pafy

# Set Pafy to use internal backend as fallback
os.environ["PAFY_BACKEND"] = "internal"

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the Video API!"})

@app.route("/get_video", methods=["GET", "POST"])
def get_video():
    try:
        # Get URL from request
        url = request.args.get("url") if request.method == "GET" else request.json.get("url")
        
        if not url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Try using yt-dlp directly first (more reliable)
        try:
            ydl_opts = {
                'format': 'best',
                'quiet': True,
                'no_warnings': True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                video_url = info['url']
                
                return jsonify({
                    "title": info.get('title', 'Unknown'),
                    "duration": str(info.get('duration', 'Unknown')),
                    "direct_url": video_url
                })
                
        # Fall back to pafy if yt-dlp direct approach fails
        except Exception as ydlp_error:
            # Get video details using pafy
            video = pafy.new(url)
            best_stream = video.getbest()  # Get best available stream
            
            return jsonify({
                "title": video.title,
                "duration": video.duration,
                "direct_url": best_stream.url
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
    
