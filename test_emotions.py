#!/usr/bin/env python3
"""
Test script to check emotion detection and AI dialogue integration
"""

import time
from collections import deque
from emotion_detector import EmotionDetector
from ai_dialogue_manager import AIDialogueManager


def test_emotion_integration():
    """Test the emotion detection and AI dialogue integration"""
    print("🧪 Testing Emotion Detection and AI Dialogue Integration")
    print("=" * 60)

    # Create emotions deque like in the main game
    emotions_deque = deque(maxlen=5)

    # Simulate different emotions being detected
    test_emotions = ["happy", "sad", "angry", "surprised", "neutral"]

    print("📊 Testing with simulated emotions...")
    for emotion in test_emotions:
        emotions_deque.append(emotion)
        print(f"   Added emotion: {emotion}")
        print(f"   Deque contents: {list(emotions_deque)}")

    # Test AI dialogue manager
    print("\n🤖 Testing AI Dialogue Manager...")
    ai_manager = AIDialogueManager()

    # Test with different emotion contexts
    for emotion in ["happy", "sad", "angry", "neutral"]:
        print(f"\n--- Testing with emotion: {emotion} ---")

        player_context = f"player is testing the emotion system and seems {emotion}"

        dialogue = ai_manager.generate_npc_dialogue(
            character_name="Merchant Pete",
            character_role="friendly trader",
            player_context=player_context,
            emotion=emotion,
        )

        print(f"Generated dialogue: {dialogue}")

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_emotion_integration()
