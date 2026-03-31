def fuse_results(speech_data, emotion_data, behavior_data):
    print("Fusing multimodal results...")
    
    max_ts = 0
    for d in emotion_data + behavior_data:
        max_ts = max(max_ts, d.get("timestamp", 0))
    for s in speech_data:
        max_ts = max(max_ts, s.get("end", 0))
        
    timeline = []
    for t in range(int(max_ts) + 2):
        ts = float(t)
        
        # Speech
        speech_text = ""
        speech_conf = 1.0
        for seg in speech_data:
            if seg["start"] <= ts <= seg["end"] + 1.0:
                speech_text = seg["text"]
                speech_conf = seg["confidence"]
                break
                
        # Emotion
        emotion = "neutral"
        close_emotions = [e for e in emotion_data if abs(e["timestamp"] - ts) < 1.0]
        if close_emotions:
            best_e = min(close_emotions, key=lambda x: abs(x["timestamp"] - ts))
            emotion = best_e["emotion"]
            
        # Behavior
        behavior = "stable"
        close_behaviors = [b for b in behavior_data if abs(b["timestamp"] - ts) < 1.0]
        if close_behaviors:
            best_b = min(close_behaviors, key=lambda x: abs(x["timestamp"] - ts))
            behavior = best_b["behavior"]
            
        # Insights Configuration
        insight = "Normal behavior"
        if emotion == "sad" and speech_conf < 0.7:
            insight = "Possible hesitation or discomfort"
        elif emotion == "angry":
            insight = "Strong emotional expression"
        elif behavior == "fidgeting":
            insight = "Nervous behavior"
        elif behavior == "moving":
            insight = "Active movement"
            
        timeline.append({
            "timestamp": ts,
            "speech": speech_text,
            "emotion": emotion,
            "behavior": behavior,
            "insight": insight
        })
        
    return timeline
