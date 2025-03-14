#!/usr/bin/env python3
"""
YouTube Automation Tool

This tool automates various YouTube tasks:
- Downloading videos
- Extracting audio
- Extracting metadata
- Generating transcripts
- Creating thumbnails
- Analyzing engagement metrics
- Scheduling uploads

NOTE: This is a sample script for testing only and requires additional
dependencies to be fully functional.
"""

import os
import sys
import json
import time
import argparse
import re
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('youtube_automator.log')
    ]
)

logger = logging.getLogger('youtube_automator')

# Mock data for testing without actual API connections
MOCK_VIDEO_DATA = {
    "dQw4w9WgXcQ": {
        "title": "Rick Astley - Never Gonna Give You Up",
        "channel": "Rick Astley",
        "views": 1234567890,
        "likes": 12345678,
        "dislikes": 123456,
        "upload_date": "2009-10-25",
        "duration": 213,  # seconds
        "description": "Rick Astley's official music video for Never Gonna Give You Up",
        "tags": ["Rick Astley", "music", "pop", "80s"],
        "comments": [
            {"author": "User1", "text": "This is a great song!", "likes": 1234},
            {"author": "User2", "text": "Classic!", "likes": 567},
        ]
    },
    "9bZkp7q19f0": {
        "title": "PSY - GANGNAM STYLE(강남스타일)",
        "channel": "PSY",
        "views": 4567890123,
        "likes": 45678901,
        "dislikes": 456789,
        "upload_date": "2012-07-15",
        "duration": 253,  # seconds
        "description": "PSY - GANGNAM STYLE(강남스타일) Official Music Video",
        "tags": ["PSY", "Gangnam Style", "K-pop", "music"],
        "comments": [
            {"author": "User3", "text": "Still watching in 2023!", "likes": 7890},
            {"author": "User4", "text": "Never gets old", "likes": 1234},
        ]
    }
}

class YouTubeAutomator:
    """Main class for YouTube automation tasks."""
    
    def __init__(self, api_key: Optional[str] = None, work_dir: Optional[str] = None):
        """Initialize the automator.
        
        Args:
            api_key: YouTube API key (optional for mock mode)
            work_dir: Working directory for downloaded files
        """
        self.api_key = api_key
        self.mock_mode = api_key is None
        if self.mock_mode:
            logger.warning("Running in MOCK MODE - no actual API calls will be made")
        
        # Set up working directory
        if work_dir:
            self.work_dir = Path(work_dir)
        else:
            self.work_dir = Path.home() / "youtube_automation"
        
        self.work_dir.mkdir(exist_ok=True, parents=True)
        logger.info(f"Working directory: {self.work_dir}")
        
        # Create subdirectories
        self.video_dir = self.work_dir / "videos"
        self.audio_dir = self.work_dir / "audio"
        self.transcript_dir = self.work_dir / "transcripts"
        self.thumbnail_dir = self.work_dir / "thumbnails"
        self.metadata_dir = self.work_dir / "metadata"
        
        for directory in [self.video_dir, self.audio_dir, self.transcript_dir, 
                          self.thumbnail_dir, self.metadata_dir]:
            directory.mkdir(exist_ok=True)
        
        # Track processed videos
        self.processed_videos = []
    
    def _get_video_data(self, video_id: str) -> Dict[str, Any]:
        """Get video data from YouTube API or mock data.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Dictionary of video metadata
            
        Raises:
            ValueError: If video ID is not found
        """
        if self.mock_mode:
            # Use mock data
            if video_id in MOCK_VIDEO_DATA:
                return MOCK_VIDEO_DATA[video_id]
            else:
                # Generate random data for unknown videos
                return {
                    "title": f"Video {video_id}",
                    "channel": f"Channel {video_id[:5]}",
                    "views": random.randint(1000, 10000000),
                    "likes": random.randint(100, 1000000),
                    "dislikes": random.randint(10, 10000),
                    "upload_date": "2023-01-01",
                    "duration": random.randint(60, 600),
                    "description": f"Description for video {video_id}",
                    "tags": ["tag1", "tag2", "tag3"],
                    "comments": [
                        {"author": "RandomUser1", "text": "Great video!", "likes": random.randint(1, 1000)},
                        {"author": "RandomUser2", "text": "Thanks for sharing!", "likes": random.randint(1, 1000)},
                    ]
                }
        else:
            # In a real implementation, this would use the YouTube API
            # For example, using the googleapiclient library
            raise NotImplementedError("Real API mode not implemented, use mock mode")
    
    def _validate_video_id(self, video_id: str) -> bool:
        """Validate that a string is a proper YouTube video ID.
        
        Args:
            video_id: String to validate
            
        Returns:
            True if valid, False otherwise
        """
        # YouTube IDs are 11 characters long and contain alphanumeric chars, '-', and '_'
        return bool(re.match(r'^[A-Za-z0-9_-]{11}$', video_id))
    
    def _extract_video_id(self, url: str) -> str:
        """Extract video ID from a YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID
            
        Raises:
            ValueError: If URL is invalid
        """
        # Try several URL formats
        patterns = [
            r'youtube\.com/watch\?v=([A-Za-z0-9_-]{11})',
            r'youtu\.be/([A-Za-z0-9_-]{11})',
            r'youtube\.com/embed/([A-Za-z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Check if the input itself is a valid video ID
        if self._validate_video_id(url):
            return url
        
        raise ValueError(f"Invalid YouTube URL or video ID: {url}")
    
    def download_video(self, video_url: str, quality: str = "high") -> str:
        """Download a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            quality: Video quality ('low', 'medium', 'high')
            
        Returns:
            Path to downloaded video file
            
        Raises:
            ValueError: If URL is invalid or video cannot be downloaded
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Downloading video {video_id} at {quality} quality")
        
        if self.mock_mode:
            # Simulate download delay based on quality
            delay = {"low": 1, "medium": 2, "high": 3}
            time.sleep(delay.get(quality, 2))
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Create a mock video file
            output_path = self.video_dir / f"{video_id}_{quality}.mp4"
            with open(output_path, "w") as f:
                f.write(f"MOCK VIDEO CONTENT: {video_data['title']}")
            
            logger.info(f"Video downloaded to {output_path}")
            
            # Save metadata
            self._save_metadata(video_id, video_data)
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "download",
                "quality": quality,
                "timestamp": datetime.now().isoformat()
            })
            
            return str(output_path)
        else:
            # In a real implementation, this would use youtube-dl, pytube or similar
            raise NotImplementedError("Real download not implemented, use mock mode")
    
    def extract_audio(self, video_url: str, format: str = "mp3", bitrate: str = "192k") -> str:
        """Extract audio from a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            format: Audio format ('mp3', 'aac', 'wav')
            bitrate: Audio bitrate ('128k', '192k', '320k')
            
        Returns:
            Path to extracted audio file
            
        Raises:
            ValueError: If URL is invalid or audio cannot be extracted
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Extracting {format} audio at {bitrate} from video {video_id}")
        
        if self.mock_mode:
            # Simulate extraction delay
            time.sleep(1.5)
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Create a mock audio file
            output_path = self.audio_dir / f"{video_id}.{format}"
            with open(output_path, "w") as f:
                f.write(f"MOCK AUDIO CONTENT: {video_data['title']} at {bitrate}")
            
            logger.info(f"Audio extracted to {output_path}")
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "extract_audio",
                "format": format,
                "bitrate": bitrate,
                "timestamp": datetime.now().isoformat()
            })
            
            return str(output_path)
        else:
            # In a real implementation, this would use ffmpeg or similar
            raise NotImplementedError("Real audio extraction not implemented, use mock mode")
    
    def get_transcript(self, video_url: str, language: str = "en") -> str:
        """Get transcript for a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            language: Language code for transcript
            
        Returns:
            Path to transcript file
            
        Raises:
            ValueError: If URL is invalid or transcript is not available
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Getting {language} transcript for video {video_id}")
        
        if self.mock_mode:
            # Simulate processing delay
            time.sleep(1)
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Generate mock transcript
            sentences = [
                "This is a sample transcript.",
                "It is automatically generated.",
                "The quality may vary.",
                "Thanks for watching this video!",
                f"The title of this video is {video_data['title']}.",
                f"It was uploaded by {video_data['channel']}.",
                "Please like and subscribe for more content.",
                "Don't forget to hit the notification bell."
            ]
            
            # Create a mock transcript file
            output_path = self.transcript_dir / f"{video_id}_{language}.txt"
            with open(output_path, "w") as f:
                duration = video_data["duration"]
                time_per_sentence = duration / len(sentences)
                
                for i, sentence in enumerate(sentences):
                    start_time = i * time_per_sentence
                    end_time = (i + 1) * time_per_sentence
                    timestamp = f"[{self._format_timestamp(start_time)} --> {self._format_timestamp(end_time)}]"
                    f.write(f"{timestamp} {sentence}\n")
            
            logger.info(f"Transcript saved to {output_path}")
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "get_transcript",
                "language": language,
                "timestamp": datetime.now().isoformat()
            })
            
            return str(output_path)
        else:
            # In a real implementation, this would use youtube_transcript_api or similar
            raise NotImplementedError("Real transcript download not implemented, use mock mode")
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format seconds as HH:MM:SS.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted timestamp
        """
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    
    def generate_thumbnail(self, video_url: str, timestamp: Optional[int] = None) -> str:
        """Generate a thumbnail from a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            timestamp: Timestamp in seconds to use for thumbnail
            
        Returns:
            Path to thumbnail image
            
        Raises:
            ValueError: If URL is invalid or thumbnail cannot be generated
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Generating thumbnail for video {video_id}")
        
        if self.mock_mode:
            # Simulate processing delay
            time.sleep(1)
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Create a mock thumbnail file
            timestamp_str = f"at_{timestamp}s" if timestamp else "default"
            output_path = self.thumbnail_dir / f"{video_id}_{timestamp_str}.jpg"
            with open(output_path, "w") as f:
                f.write(f"MOCK THUMBNAIL: {video_data['title']} {timestamp_str}")
            
            logger.info(f"Thumbnail saved to {output_path}")
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "generate_thumbnail",
                "timestamp_used": timestamp,
                "timestamp": datetime.now().isoformat()
            })
            
            return str(output_path)
        else:
            # In a real implementation, this would use ffmpeg or similar
            raise NotImplementedError("Real thumbnail generation not implemented, use mock mode")
    
    def _save_metadata(self, video_id: str, metadata: Dict[str, Any]) -> str:
        """Save video metadata to a file.
        
        Args:
            video_id: YouTube video ID
            metadata: Video metadata
            
        Returns:
            Path to metadata file
        """
        output_path = self.metadata_dir / f"{video_id}_metadata.json"
        with open(output_path, "w") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Metadata saved to {output_path}")
        return str(output_path)
    
    def get_video_metadata(self, video_url: str) -> Dict[str, Any]:
        """Get metadata for a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            
        Returns:
            Dictionary of video metadata
            
        Raises:
            ValueError: If URL is invalid
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Getting metadata for video {video_id}")
        
        if self.mock_mode:
            # Simulate API delay
            time.sleep(0.5)
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Save metadata to file
            self._save_metadata(video_id, video_data)
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "get_metadata",
                "timestamp": datetime.now().isoformat()
            })
            
            return video_data
        else:
            # In a real implementation, this would use the YouTube API
            raise NotImplementedError("Real metadata retrieval not implemented, use mock mode")
    
    def analyze_engagement(self, video_url: str) -> Dict[str, Any]:
        """Analyze engagement metrics for a YouTube video.
        
        Args:
            video_url: YouTube URL or video ID
            
        Returns:
            Dictionary of engagement metrics and analysis
            
        Raises:
            ValueError: If URL is invalid
        """
        try:
            video_id = self._extract_video_id(video_url)
        except ValueError as e:
            logger.error(f"Failed to extract video ID: {e}")
            raise
        
        logger.info(f"Analyzing engagement for video {video_id}")
        
        if self.mock_mode:
            # Simulate processing delay
            time.sleep(1.5)
            
            # Get mock video data
            video_data = self._get_video_data(video_id)
            
            # Calculate engagement metrics
            views = video_data["views"]
            likes = video_data["likes"]
            dislikes = video_data["dislikes"]
            total_reactions = likes + dislikes
            
            engagement_metrics = {
                "views": views,
                "likes": likes,
                "dislikes": dislikes,
                "like_ratio": likes / total_reactions if total_reactions > 0 else 0,
                "engagement_rate": total_reactions / views if views > 0 else 0,
                "comments": len(video_data["comments"]),
                "estimated_watch_time": (views * video_data["duration"] * 0.4) / 3600,  # hours, assuming 40% retention
                "performance_score": random.randint(1, 100),
                "audience_retention": {
                    "average": random.uniform(0.3, 0.7),
                    "graph": [random.uniform(0.7, 1.0)] + 
                             [random.uniform(0.4, 0.8) for _ in range(8)] + 
                             [random.uniform(0.2, 0.5)]
                }
            }
            
            # Add some analysis
            analysis = {
                "summary": self._get_engagement_summary(engagement_metrics),
                "suggestions": self._get_improvement_suggestions(engagement_metrics),
                "comparison": {
                    "channel_average": random.uniform(0.8, 1.2),
                    "category_average": random.uniform(0.8, 1.2)
                }
            }
            
            result = {
                "video_id": video_id,
                "title": video_data["title"],
                "metrics": engagement_metrics,
                "analysis": analysis
            }
            
            # Save analysis
            output_path = self.metadata_dir / f"{video_id}_engagement.json"
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Engagement analysis saved to {output_path}")
            
            # Track processed video
            self.processed_videos.append({
                "id": video_id,
                "title": video_data["title"],
                "action": "analyze_engagement",
                "timestamp": datetime.now().isoformat()
            })
            
            return result
        else:
            # In a real implementation, this would use the YouTube Analytics API
            raise NotImplementedError("Real engagement analysis not implemented, use mock mode")
    
    def _get_engagement_summary(self, metrics: Dict[str, Any]) -> str:
        """Generate a summary of engagement metrics.
        
        Args:
            metrics: Engagement metrics
            
        Returns:
            Summary string
        """
        like_ratio = metrics["like_ratio"] * 100
        engagement_rate = metrics["engagement_rate"] * 100
        
        if like_ratio > 95:
            like_sentiment = "extremely positive"
        elif like_ratio > 90:
            like_sentiment = "very positive"
        elif like_ratio > 80:
            like_sentiment = "positive"
        elif like_ratio > 70:
            like_sentiment = "mostly positive"
        else:
            like_sentiment = "mixed"
        
        if engagement_rate > 10:
            engagement_level = "extremely high"
        elif engagement_rate > 5:
            engagement_level = "very high"
        elif engagement_rate > 3:
            engagement_level = "good"
        elif engagement_rate > 1:
            engagement_level = "average"
        else:
            engagement_level = "below average"
        
        return (f"This video has {metrics['views']:,} views with a {like_sentiment} audience sentiment "
                f"({like_ratio:.1f}% like ratio) and {engagement_level} engagement rate ({engagement_rate:.2f}%). "
                f"It has received {metrics['comments']} comments and has an estimated watch time of "
                f"{metrics['estimated_watch_time']:.1f} hours.")
    
    def _get_improvement_suggestions(self, metrics: Dict[str, Any]) -> List[str]:
        """Generate improvement suggestions based on metrics.
        
        Args:
            metrics: Engagement metrics
            
        Returns:
            List of suggestions
        """
        suggestions = []
        
        if metrics["like_ratio"] < 0.8:
            suggestions.append("Consider addressing concerns that may be causing dislikes.")
        
        if metrics["engagement_rate"] < 0.03:
            suggestions.append("Try adding a call to action to encourage more engagement.")
        
        if metrics["audience_retention"]["average"] < 0.5:
            suggestions.append("Review content pacing to improve audience retention.")
        
        # Add some random suggestions
        random_suggestions = [
            "Optimize your thumbnail for better click-through rate.",
            "Add timestamps to your video description.",
            "Include cards and end screens to promote related content.",
            "Respond to top comments to boost engagement.",
            "Try a more specific title to attract your target audience.",
            "Improve lighting and audio quality for better viewer experience.",
            "Consider adding subtitles to reach a wider audience."
        ]
        
        suggestions.extend(random.sample(random_suggestions, min(3, len(random_suggestions))))
        return suggestions
    
    def schedule_upload(self, video_path: str, metadata: Dict[str, Any], 
                         publish_time: Optional[datetime] = None) -> Dict[str, Any]:
        """Schedule a video upload to YouTube.
        
        Args:
            video_path: Path to video file
            metadata: Video metadata (title, description, etc.)
            publish_time: Time to publish the video
            
        Returns:
            Dictionary with upload details
            
        Raises:
            ValueError: If video file or metadata is invalid
            FileNotFoundError: If video file doesn't exist
        """
        video_path = Path(video_path)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_path}")
        
        required_fields = ["title", "description", "tags", "category"]
        missing_fields = [field for field in required_fields if field not in metadata]
        if missing_fields:
            raise ValueError(f"Missing required metadata fields: {', '.join(missing_fields)}")
        
        # Set default publish time if not provided
        if publish_time is None:
            # Default to next day at noon
            publish_time = datetime.now().replace(hour=12, minute=0, second=0) + timedelta(days=1)
        
        logger.info(f"Scheduling upload of '{metadata['title']}' for {publish_time}")
        
        if self.mock_mode:
            # Simulate upload preparation
            time.sleep(2)
            
            upload_id = f"up{random.randint(10000, 99999)}"
            
            result = {
                "upload_id": upload_id,
                "title": metadata["title"],
                "file": str(video_path),
                "publish_time": publish_time.isoformat(),
                "status": "scheduled",
                "estimated_processing_time": random.randint(5, 120),  # minutes
                "video_id": None,  # Will be assigned after upload
                "upload_url": None  # Will be assigned after upload
            }
            
            # Save upload details
            output_path = self.metadata_dir / f"{upload_id}_upload.json"
            with open(output_path, "w") as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Upload scheduled! Details saved to {output_path}")
            return result
        else:
            # In a real implementation, this would use the YouTube API
            raise NotImplementedError("Real video uploading not implemented, use mock mode")
    
    def batch_process(self, video_urls: List[str], actions: List[str]) -> Dict[str, List[str]]:
        """Process multiple videos with multiple actions.
        
        Args:
            video_urls: List of YouTube URLs or video IDs
            actions: List of actions to perform ('download', 'extract_audio', 
                     'get_transcript', 'get_metadata', 'generate_thumbnail', 
                     'analyze_engagement')
            
        Returns:
            Dictionary mapping actions to lists of output paths
            
        Raises:
            ValueError: If an invalid URL or action is provided
        """
        valid_actions = ['download', 'extract_audio', 'get_transcript', 
                          'get_metadata', 'generate_thumbnail', 'analyze_engagement']
        
        invalid_actions = [action for action in actions if action not in valid_actions]
        if invalid_actions:
            raise ValueError(f"Invalid actions: {', '.join(invalid_actions)}")
        
        logger.info(f"Batch processing {len(video_urls)} videos with actions: {', '.join(actions)}")
        
        results = {action: [] for action in actions}
        
        for video_url in video_urls:
            try:
                video_id = self._extract_video_id(video_url)
                logger.info(f"Processing video {video_id}")
                
                for action in actions:
                    if action == 'download':
                        output_path = self.download_video(video_id)
                        results[action].append(output_path)
                    elif action == 'extract_audio':
                        output_path = self.extract_audio(video_id)
                        results[action].append(output_path)
                    elif action == 'get_transcript':
                        output_path = self.get_transcript(video_id)
                        results[action].append(output_path)
                    elif action == 'get_metadata':
                        metadata = self.get_video_metadata(video_id)
                        results[action].append(self.metadata_dir / f"{video_id}_metadata.json")
                    elif action == 'generate_thumbnail':
                        output_path = self.generate_thumbnail(video_id)
                        results[action].append(output_path)
                    elif action == 'analyze_engagement':
                        analysis = self.analyze_engagement(video_id)
                        results[action].append(self.metadata_dir / f"{video_id}_engagement.json")
            except Exception as e:
                logger.error(f"Error processing video {video_url}: {e}")
                # Continue with next video
        
        return results
    
    def get_processing_history(self) -> List[Dict[str, Any]]:
        """Get history of processed videos.
        
        Returns:
            List of processing records
        """
        return self.processed_videos

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description="YouTube Automation Tool")
    
    # Main arguments
    parser.add_argument("--api-key", help="YouTube API key (leave empty for mock mode)")
    parser.add_argument("--work-dir", help="Working directory for downloaded files")
    
    # Action subparsers
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Download video
    download_parser = subparsers.add_parser("download", help="Download a YouTube video")
    download_parser.add_argument("video_url", help="YouTube URL or video ID")
    download_parser.add_argument("--quality", choices=["low", "medium", "high"], 
                                default="high", help="Video quality")
    
    # Extract audio
    audio_parser = subparsers.add_parser("extract-audio", help="Extract audio from a YouTube video")
    audio_parser.add_argument("video_url", help="YouTube URL or video ID")
    audio_parser.add_argument("--format", choices=["mp3", "aac", "wav"], 
                             default="mp3", help="Audio format")
    audio_parser.add_argument("--bitrate", choices=["128k", "192k", "320k"], 
                             default="192k", help="Audio bitrate")
    
    # Get transcript
    transcript_parser = subparsers.add_parser("get-transcript", help="Get transcript for a YouTube video")
    transcript_parser.add_argument("video_url", help="YouTube URL or video ID")
    transcript_parser.add_argument("--language", default="en", help="Language code for transcript")
    
    # Get metadata
    metadata_parser = subparsers.add_parser("get-metadata", help="Get metadata for a YouTube video")
    metadata_parser.add_argument("video_url", help="YouTube URL or video ID")
    
    # Generate thumbnail
    thumbnail_parser = subparsers.add_parser("generate-thumbnail", help="Generate a thumbnail from a video")
    thumbnail_parser.add_argument("video_url", help="YouTube URL or video ID")
    thumbnail_parser.add_argument("--timestamp", type=int, help="Timestamp in seconds for thumbnail")
    
    # Analyze engagement
    engagement_parser = subparsers.add_parser("analyze-engagement", help="Analyze video engagement metrics")
    engagement_parser.add_argument("video_url", help="YouTube URL or video ID")
    
    # Batch process
    batch_parser = subparsers.add_parser("batch", help="Process multiple videos with multiple actions")
    batch_parser.add_argument("--video-urls", nargs="+", required=True, help="List of YouTube URLs or video IDs")
    batch_parser.add_argument("--actions", nargs="+", required=True, 
                             choices=["download", "extract_audio", "get_transcript", "get_metadata", 
                                      "generate_thumbnail", "analyze_engagement"],
                             help="List of actions to perform")
    
    # History
    subparsers.add_parser("history", help="Show processing history")
    
    return parser.parse_args()

def main() -> None:
    """Main entry point for the YouTube automator."""
    args = parse_args()
    
    try:
        # Initialize automator
        automator = YouTubeAutomator(api_key=args.api_key, work_dir=args.work_dir)
        
        # Perform action
        if args.action == "download":
            output_path = automator.download_video(args.video_url, args.quality)
            print(f"Video downloaded to {output_path}")
        
        elif args.action == "extract-audio":
            output_path = automator.extract_audio(args.video_url, args.format, args.bitrate)
            print(f"Audio extracted to {output_path}")
        
        elif args.action == "get-transcript":
            output_path = automator.get_transcript(args.video_url, args.language)
            print(f"Transcript saved to {output_path}")
        
        elif args.action == "get-metadata":
            metadata = automator.get_video_metadata(args.video_url)
            print(json.dumps(metadata, indent=2))
        
        elif args.action == "generate-thumbnail":
            output_path = automator.generate_thumbnail(args.video_url, args.timestamp)
            print(f"Thumbnail saved to {output_path}")
        
        elif args.action == "analyze-engagement":
            analysis = automator.analyze_engagement(args.video_url)
            print(f"Summary: {analysis['analysis']['summary']}")
            print("\nSuggestions:")
            for suggestion in analysis['analysis']['suggestions']:
                print(f"- {suggestion}")
        
        elif args.action == "batch":
            results = automator.batch_process(args.video_urls, args.actions)
            for action, outputs in results.items():
                print(f"\n{action.capitalize()} outputs:")
                for output in outputs:
                    print(f"- {output}")
        
        elif args.action == "history":
            history = automator.get_processing_history()
            if not history:
                print("No processing history yet.")
            else:
                for i, record in enumerate(history, 1):
                    print(f"{i}. [{record['timestamp']}] {record['action']} - {record['title']} ({record['id']})")
        
        else:
            # No action specified, show help
            print("No action specified. Use --help to see available actions.")
    
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()