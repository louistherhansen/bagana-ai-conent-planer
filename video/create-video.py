#!/usr/bin/env python3
"""
BAGANA AI Video Tutorial Creator
Automates video creation from assets using MoviePy

Requirements:
    pip install moviepy pillow

Usage:
    python create-video.py
"""

import os
from pathlib import Path
from typing import Optional

try:
    from moviepy.editor import (
        VideoFileClip,
        ImageClip,
        TextClip,
        CompositeVideoClip,
        AudioFileClip,
        concatenate_videoclips,
        ColorClip,
    )
    from moviepy.video.fx import fadein, fadeout
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("MoviePy not installed. Install with: pip install moviepy")

# Configuration
VIDEO_DURATION = 60  # seconds
RESOLUTION = (1920, 1080)
FPS = 30
OUTPUT_FILE = "bagana-ai-tutorial.mp4"

# Scene timings (in seconds)
SCENE_TIMINGS = {
    "opening": (0, 5),
    "problem": (5, 20),
    "solution": (20, 45),
    "value": (45, 55),
    "cta": (55, 60),
}

# Asset paths (relative to video/ directory)
ASSET_PATHS = {
    "logo": "../bagana-ai-logo.png",  # Updated path
    "voiceover": "voiceover.mp3",  # User needs to provide this
    "background_music": "background-music.mp3",  # Optional
    "screenshots": {
        "chat": "assets/chat-interface.png",
        "dashboard": "assets/dashboard.png",
        "plans": "assets/content-plans.png",
        "sentiment": "assets/sentiment-analysis.png",
        "trends": "assets/trends-view.png",
    },
}


def check_assets() -> dict:
    """Check which assets are available."""
    base_dir = Path(__file__).parent
    assets_status = {
        "logo": (base_dir / ASSET_PATHS["logo"]).exists(),
        "voiceover": (base_dir / ASSET_PATHS["voiceover"]).exists(),
        "background_music": (base_dir / ASSET_PATHS["background_music"]).exists(),
        "screenshots": {},
    }
    
    for key, path in ASSET_PATHS["screenshots"].items():
        assets_status["screenshots"][key] = (base_dir / path).exists()
    
    return assets_status


def create_opening_scene(duration: float = 5.0) -> Optional[ImageClip]:
    """Create opening scene with logo."""
    base_dir = Path(__file__).parent
    logo_path = base_dir / ASSET_PATHS["logo"]
    
    if not logo_path.exists():
        print(f"⚠️  Logo not found at {logo_path}")
        print("   Creating placeholder...")
        # Create placeholder
        clip = ColorClip(size=RESOLUTION, color=(20, 150, 150), duration=duration)
        text = TextClip(
            "BAGANA AI",
            fontsize=80,
            color="white",
            font="Arial-Bold",
        ).set_position("center").set_duration(duration)
        return CompositeVideoClip([clip, text])
    
    logo = ImageClip(str(logo_path)).set_duration(duration)
    logo = logo.resize(height=400).set_position("center")
    
    # Add fade in
    logo = logo.fadein(0.5)
    
    # Add tagline text
    tagline = TextClip(
        "AI-Powered Content Strategy Platform",
        fontsize=40,
        color="white",
        font="Arial",
    ).set_position(("center", RESOLUTION[1] // 2 + 250)).set_duration(duration).fadein(0.8)
    
    # Background
    bg = ColorClip(size=RESOLUTION, color=(20, 150, 150), duration=duration)
    
    return CompositeVideoClip([bg, logo, tagline])


def create_problem_scene(duration: float = 15.0) -> Optional[ColorClip]:
    """Create problem visualization scene."""
    # Placeholder - user should replace with actual visuals
    clip = ColorClip(size=RESOLUTION, color=(50, 50, 50), duration=duration)
    
    text1 = TextClip(
        "Multiple tools. Scattered data.",
        fontsize=60,
        color="white",
        font="Arial-Bold",
    ).set_position(("center", RESOLUTION[1] // 2 - 50)).set_duration(duration).fadein(0.5)
    
    text2 = TextClip(
        "Time-consuming.",
        fontsize=60,
        color="white",
        font="Arial-Bold",
    ).set_position(("center", RESOLUTION[1] // 2 + 50)).set_duration(duration).fadein(1.0)
    
    return CompositeVideoClip([clip, text1, text2])


def create_solution_scene(duration: float = 25.0) -> Optional[ColorClip]:
    """Create solution demo scene."""
    # This should show platform screenshots
    # For now, create placeholder with text
    
    clip = ColorClip(size=RESOLUTION, color=(240, 250, 250), duration=duration)
    
    texts = [
        ("One Platform", 0, 5),
        ("Multi-Agent System", 5, 10),
        ("Content Plans", 10, 15),
        ("Sentiment Analysis", 15, 20),
        ("Trend Insights", 20, 25),
    ]
    
    text_clips = []
    for text, start, end in texts:
        txt = TextClip(
            text,
            fontsize=70,
            color=(20, 150, 150),
            font="Arial-Bold",
        ).set_position("center").set_start(start).set_duration(end - start).fadein(0.3).fadeout(0.3)
        text_clips.append(txt)
    
    return CompositeVideoClip([clip] + text_clips)


def create_value_scene(duration: float = 10.0) -> Optional[ColorClip]:
    """Create value proposition scene."""
    clip = ColorClip(size=RESOLUTION, color=(250, 250, 250), duration=duration)
    
    benefits = [
        "⏱️  Save Hours",
        "📊  Data-Driven",
        "🎯  Consistent Messaging",
        "📈  Scale Effortlessly",
    ]
    
    text_clips = []
    y_start = RESOLUTION[1] // 2 - 150
    for i, benefit in enumerate(benefits):
        txt = TextClip(
            benefit,
            fontsize=50,
            color=(20, 150, 150),
            font="Arial-Bold",
        ).set_position(("center", y_start + i * 80)).set_duration(duration).fadein(0.5)
        text_clips.append(txt)
    
    return CompositeVideoClip([clip] + text_clips)


def create_cta_scene(duration: float = 5.0) -> Optional[ColorClip]:
    """Create call-to-action scene."""
    clip = ColorClip(size=RESOLUTION, color=(20, 150, 150), duration=duration)
    
    cta_text = TextClip(
        "Get Started Today",
        fontsize=70,
        color="white",
        font="Arial-Bold",
    ).set_position(("center", RESOLUTION[1] // 2 - 50)).set_duration(duration).fadein(0.3)
    
    url_text = TextClip(
        "github.com/louistherhansen/bagana-ai-conent-planer",
        fontsize=30,
        color="white",
        font="Arial",
    ).set_position(("center", RESOLUTION[1] // 2 + 50)).set_duration(duration).fadein(0.5)
    
    return CompositeVideoClip([clip, cta_text, url_text])


def create_video() -> Optional[str]:
    """Main function to create the video."""
    if not MOVIEPY_AVAILABLE:
        print("❌ MoviePy is not installed.")
        print("   Install it with: pip install moviepy pillow")
        return None
    
    print("🎬 BAGANA AI Video Tutorial Creator")
    print("=" * 50)
    
    # Check assets
    print("\n📋 Checking assets...")
    assets = check_assets()
    
    if not assets["logo"]:
        print("⚠️  Logo not found. Will use placeholder.")
    if not assets["voiceover"]:
        print("⚠️  Voiceover not found. Video will be silent.")
        print("   Place voiceover.mp3 in the video/ directory.")
    
    print("\n🎥 Creating video scenes...")
    
    # Create scenes
    scenes = []
    
    try:
        print("  Creating opening scene...")
        opening = create_opening_scene(5.0)
        if opening:
            scenes.append(opening)
        
        print("  Creating problem scene...")
        problem = create_problem_scene(15.0)
        if problem:
            scenes.append(problem)
        
        print("  Creating solution scene...")
        solution = create_solution_scene(25.0)
        if solution:
            scenes.append(solution)
        
        print("  Creating value scene...")
        value = create_value_scene(10.0)
        if value:
            scenes.append(value)
        
        print("  Creating CTA scene...")
        cta = create_cta_scene(5.0)
        if cta:
            scenes.append(cta)
        
        if not scenes:
            print("❌ No scenes created. Check asset paths.")
            return None
        
        print(f"\n📹 Concatenating {len(scenes)} scenes...")
        final_video = concatenate_videoclips(scenes, method="compose")
        
        # Add audio if available
        base_dir = Path(__file__).parent
        voiceover_path = base_dir / ASSET_PATHS["voiceover"]
        
        if voiceover_path.exists():
            print("🎵 Adding voiceover...")
            audio = AudioFileClip(str(voiceover_path))
            # Trim audio to match video duration
            if audio.duration > final_video.duration:
                audio = audio.subclip(0, final_video.duration)
            final_video = final_video.set_audio(audio)
        else:
            print("⚠️  No voiceover found. Adding background music if available...")
            music_path = base_dir / ASSET_PATHS["background_music"]
            if music_path.exists():
                music = AudioFileClip(str(music_path))
                if music.duration > final_video.duration:
                    music = music.subclip(0, final_video.duration)
                music = music.volumex(0.3)  # Lower volume
                final_video = final_video.set_audio(music)
        
        # Set FPS
        final_video = final_video.set_fps(FPS)
        
        # Export
        output_path = base_dir / OUTPUT_FILE
        print(f"\n💾 Exporting to {output_path}...")
        print("   This may take a few minutes...")
        
        final_video.write_videofile(
            str(output_path),
            fps=FPS,
            codec="libx264",
            audio_codec="aac",
            bitrate="8000k",
            preset="medium",
        )
        
        print(f"\n✅ Video created successfully!")
        print(f"   Output: {output_path}")
        print(f"   Duration: {final_video.duration:.1f} seconds")
        
        return str(output_path)
        
    except Exception as e:
        print(f"\n❌ Error creating video: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    result = create_video()
    if result:
        print("\n🎉 Done! Review the video and make adjustments as needed.")
    else:
        print("\n⚠️  Video creation failed. Check the errors above.")
