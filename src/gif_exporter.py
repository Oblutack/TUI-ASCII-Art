"""
GIF ASCII Art Export Module
Exports animated ASCII art in various formats
"""

import os
from pathlib import Path
from typing import List, Tuple
from rich.text import Text


class GifExporter:
    """Handles exporting ASCII GIF animations to various formats"""
    
    @staticmethod
    def clean_ansi(text: str) -> str:
        """Remove ANSI codes from text"""
        try:
            return Text.from_ansi(text).plain
        except:
            # Fallback: simple ANSI removal
            import re
            ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
            return ansi_escape.sub('', text)
    
    @staticmethod
    def export_to_single_txt(frames: List[str], delays: List[int], output_path: str) -> bool:
        """
        Export all frames to a single text file with separators
        
        Args:
            frames: List of ASCII art frames
            delays: List of frame delays in milliseconds
            output_path: Output file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Write header
                f.write("=" * 80 + "\n")
                f.write("ASCII ART ANIMATION\n")
                f.write(f"Total Frames: {len(frames)}\n")
                f.write("=" * 80 + "\n\n")
                
                # Write each frame
                for i, (frame, delay) in enumerate(zip(frames, delays)):
                    f.write(f"\n{'─' * 80}\n")
                    f.write(f"FRAME {i + 1}/{len(frames)} | Delay: {delay}ms\n")
                    f.write(f"{'─' * 80}\n\n")
                    
                    # Clean ANSI codes
                    clean_frame = GifExporter.clean_ansi(frame)
                    f.write(clean_frame)
                    f.write("\n\n")
                
                # Write footer
                f.write("=" * 80 + "\n")
                f.write("END OF ANIMATION\n")
                f.write("=" * 80 + "\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to TXT: {e}")
            return False
    
    @staticmethod
    def export_to_html(frames: List[str], delays: List[int], output_path: str) -> bool:
        """
        Export as interactive HTML with JavaScript player
        
        Args:
            frames: List of ASCII art frames
            delays: List of frame delays in milliseconds
            output_path: Output HTML file path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clean frames from ANSI
            clean_frames = [GifExporter.clean_ansi(frame) for frame in frames]
            
            # Escape frames for JavaScript
            js_frames = []
            for frame in clean_frames:
                # Escape special characters
                escaped = frame.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
                js_frames.append(escaped)
            
            # Generate JavaScript array
            frames_js = ',\n'.join([f'`{frame}`' for frame in js_frames])
            delays_js = ','.join([str(d) for d in delays])
            
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ASCII Art Animation</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            font-family: 'Courier New', monospace;
            color: #a6e3a1;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .container {{
            background: rgba(17, 17, 27, 0.9);
            border: 3px solid #89b4fa;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
            max-width: 95vw;
            overflow: hidden;
        }}
        
        h1 {{
            color: #89b4fa;
            text-align: center;
            margin-bottom: 20px;
            font-size: 24px;
            text-shadow: 0 0 10px rgba(137, 180, 250, 0.5);
        }}
        
        #ascii-display {{
            background: #0d0d17;
            padding: 20px;
            border: 2px solid #45475a;
            border-radius: 8px;
            font-size: 10px;
            line-height: 1.2;
            white-space: pre;
            overflow: auto;
            max-height: 70vh;
            color: #a6e3a1;
            text-shadow: 0 0 5px rgba(166, 227, 161, 0.3);
        }}
        
        .controls {{
            margin-top: 20px;
            display: flex;
            gap: 15px;
            align-items: center;
            justify-content: center;
            flex-wrap: wrap;
        }}
        
        button {{
            background: #313244;
            color: #89b4fa;
            border: 2px solid #45475a;
            border-radius: 6px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s;
            font-family: 'Courier New', monospace;
        }}
        
        button:hover {{
            background: #45475a;
            border-color: #89b4fa;
            box-shadow: 0 0 15px rgba(137, 180, 250, 0.3);
        }}
        
        button:active {{
            transform: scale(0.95);
        }}
        
        button.active {{
            background: #89b4fa;
            color: #1e1e2e;
        }}
        
        .slider-container {{
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px;
            background: #313244;
            border-radius: 6px;
        }}
        
        .slider-container label {{
            color: #cdd6f4;
            font-size: 12px;
            min-width: 60px;
        }}
        
        input[type="range"] {{
            width: 150px;
            height: 6px;
            background: #45475a;
            border-radius: 3px;
            outline: none;
        }}
        
        input[type="range"]::-webkit-slider-thumb {{
            appearance: none;
            width: 16px;
            height: 16px;
            background: #89b4fa;
            border-radius: 50%;
            cursor: pointer;
        }}
        
        .frame-info {{
            color: #cdd6f4;
            font-size: 12px;
            padding: 8px 15px;
            background: #313244;
            border-radius: 6px;
            min-width: 100px;
            text-align: center;
        }}
        
        @media (max-width: 768px) {{
            #ascii-display {{
                font-size: 6px;
            }}
            
            .controls {{
                flex-direction: column;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>▌ ASCII ART ANIMATION</h1>
        <div id="ascii-display"></div>
        
        <div class="controls">
            <button id="playBtn" class="active">▶ PLAY</button>
            <button id="stopBtn">■ STOP</button>
            
            <div class="slider-container">
                <label>Speed:</label>
                <input type="range" id="speedSlider" min="25" max="400" value="100">
                <span id="speedValue">1.0x</span>
            </div>
            
            <label style="color: #cdd6f4; display: flex; align-items: center; gap: 8px; cursor: pointer;">
                <input type="checkbox" id="loopCheck" checked style="width: 18px; height: 18px; cursor: pointer;">
                LOOP
            </label>
            
            <div class="frame-info" id="frameInfo">Frame: 0/{len(frames)}</div>
        </div>
    </div>
    
    <script>
        // Animation data
        const frames = [
            {frames_js}
        ];
        
        const delays = [{delays_js}];
        
        // Player state
        let currentFrame = 0;
        let isPlaying = false;
        let playbackSpeed = 1.0;
        let isLooping = true;
        let animationTimeout = null;
        
        // DOM elements
        const display = document.getElementById('ascii-display');
        const playBtn = document.getElementById('playBtn');
        const stopBtn = document.getElementById('stopBtn');
        const speedSlider = document.getElementById('speedSlider');
        const speedValue = document.getElementById('speedValue');
        const loopCheck = document.getElementById('loopCheck');
        const frameInfo = document.getElementById('frameInfo');
        
        // Display frame
        function showFrame(index) {{
            if (index >= 0 && index < frames.length) {{
                display.textContent = frames[index];
                frameInfo.textContent = `Frame: ${{index + 1}}/${{frames.length}}`;
            }}
        }}
        
        // Play animation
        function play() {{
            if (!isPlaying) {{
                isPlaying = true;
                playBtn.textContent = '⏸ PAUSE';
                playBtn.classList.add('active');
                scheduleNextFrame();
            }}
        }}
        
        // Pause animation
        function pause() {{
            isPlaying = false;
            playBtn.textContent = '▶ PLAY';
            playBtn.classList.remove('active');
            if (animationTimeout) {{
                clearTimeout(animationTimeout);
            }}
        }}
        
        // Stop animation
        function stop() {{
            pause();
            currentFrame = 0;
            showFrame(currentFrame);
        }}
        
        // Schedule next frame
        function scheduleNextFrame() {{
            if (!isPlaying) return;
            
            const delay = delays[currentFrame] || 100;
            const adjustedDelay = delay / playbackSpeed;
            
            animationTimeout = setTimeout(() => {{
                currentFrame++;
                
                if (currentFrame >= frames.length) {{
                    if (isLooping) {{
                        currentFrame = 0;
                    }} else {{
                        pause();
                        return;
                    }}
                }}
                
                showFrame(currentFrame);
                scheduleNextFrame();
            }}, adjustedDelay);
        }}
        
        // Event listeners
        playBtn.addEventListener('click', () => {{
            if (isPlaying) {{
                pause();
            }} else {{
                play();
            }}
        }});
        
        stopBtn.addEventListener('click', stop);
        
        speedSlider.addEventListener('input', (e) => {{
            playbackSpeed = e.target.value / 100;
            speedValue.textContent = playbackSpeed.toFixed(1) + 'x';
        }});
        
        loopCheck.addEventListener('change', (e) => {{
            isLooping = e.target.checked;
        }});
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.code === 'Space') {{
                e.preventDefault();
                if (isPlaying) pause();
                else play();
            }} else if (e.code === 'KeyS') {{
                stop();
            }}
        }});
        
        // Initialize
        showFrame(0);
        play(); // Auto-play on load
    </script>
</body>
</html>"""
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return True
        except Exception as e:
            print(f"Error exporting to HTML: {e}")
            return False
    
    @staticmethod
    def export_to_folder(frames: List[str], delays: List[int], output_folder: str) -> bool:
        """
        Export each frame as individual text file in a folder
        
        Args:
            frames: List of ASCII art frames
            delays: List of frame delays in milliseconds
            output_folder: Output folder path
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create folder if it doesn't exist
            Path(output_folder).mkdir(parents=True, exist_ok=True)
            
            # Export each frame
            for i, (frame, delay) in enumerate(zip(frames, delays)):
                frame_path = os.path.join(output_folder, f"frame_{i+1:04d}.txt")
                clean_frame = GifExporter.clean_ansi(frame)
                
                with open(frame_path, 'w', encoding='utf-8') as f:
                    f.write(f"Frame {i+1}/{len(frames)} | Delay: {delay}ms\n")
                    f.write("=" * 80 + "\n\n")
                    f.write(clean_frame)
            
            # Create metadata file
            metadata_path = os.path.join(output_folder, "_animation_info.txt")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                f.write("ASCII ART ANIMATION METADATA\n")
                f.write("=" * 80 + "\n\n")
                f.write(f"Total Frames: {len(frames)}\n")
                f.write(f"Frame Delays (ms): {', '.join(map(str, delays))}\n")
                f.write(f"\nFrames are numbered from frame_0001.txt to frame_{len(frames):04d}.txt\n")
            
            return True
        except Exception as e:
            print(f"Error exporting to folder: {e}")
            return False