import React, { useEffect, useState } from "react";
import { 
  View, 
  Text, 
  TouchableOpacity, 
  ActivityIndicator, 
  Alert, 
  ScrollView, 
  StyleSheet,
  Dimensions,
  TextInput,
  Modal
} from "react-native";
import { useRoute, useNavigation } from "@react-navigation/native";
import { useQuery, useMutation, useAction } from "convex/react";
import { api } from "@packages/backend/convex/_generated/api";
import { Audio } from "expo-av";

const { width, height } = Dimensions.get('window');

const SongDetailsScreen = () => {
  const route = useRoute();
  const navigation = useNavigation();
  // @ts-ignore
  const { songId } = route.params || {};
  const song = useQuery(api.songs.getSong, { id: songId });
  const updateSong = useMutation(api.songs.updateSong);
  const generateSinging = useAction(api.ai_singer.generateSinging);
  
  const [sound, setSound] = useState<Audio.Sound | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoadingAudio, setIsLoadingAudio] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Remove isEditing state
  const [editedTitle, setEditedTitle] = useState("");
  const [editedLyrics, setEditedLyrics] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const [editedVoiceStyle, setEditedVoiceStyle] = useState("");
  const [editedMood, setEditedMood] = useState("");
  const [pitch, setPitch] = useState(0);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);

  useEffect(() => {
    if (song) {
      setEditedTitle(song.title);
      setEditedLyrics(song.lyrics);
      setEditedVoiceStyle(song.voiceStyle);
      setEditedMood(song.mood || "");
      setHasUnsavedChanges(false);
    }
  }, [song]);

  // Track changes to detect when regeneration is needed
  useEffect(() => {
    if (song) {
      const voiceStyleChanged = editedVoiceStyle !== song.voiceStyle;
      const moodChanged = editedMood !== (song.mood || "");
      const lyricsChanged = editedLyrics !== song.lyrics;
      const pitchChanged = pitch !== (song.pitch || 0);
      const hasChanges = voiceStyleChanged || moodChanged || lyricsChanged || pitchChanged;
      
      setHasUnsavedChanges(hasChanges);
    }
  }, [editedLyrics, editedVoiceStyle, editedMood, pitch, song]);

  const handleLyricsChange = React.useCallback((newLyrics: string) => {
    setEditedLyrics(newLyrics);
    // No auto-save while typing - only save on regenerate or back button
  }, []);



  useEffect(() => {
    return () => {
      if (sound) {
        sound.unloadAsync();
      }
    };
  }, [sound]);

  const playAudio = async () => {
    if (!song?.generatedSongUrl) return;
    setIsLoadingAudio(true);
    try {
      if (sound) {
        await sound.replayAsync();
        setIsPlaying(true);
        setIsLoadingAudio(false);
        return;
      }
      const { sound: newSound } = await Audio.Sound.createAsync({ uri: song.generatedSongUrl });
      setSound(newSound);
      await newSound.playAsync();
      setIsPlaying(true);
      
      newSound.setOnPlaybackStatusUpdate((status) => {
        if (status.isLoaded && status.didJustFinish) {
          setIsPlaying(false);
        }
      });
    } catch (err) {
      Alert.alert("Error", "Failed to play audio");
    } finally {
      setIsLoadingAudio(false);
    }
  };

  const stopAudio = async () => {
    if (sound) {
      await sound.stopAsync();
      setIsPlaying(false);
    }
  };

  const generateSong = async () => {
    if (!song) return;
    
    setIsGenerating(true);
    setError(null);
    
    try {
      // Generate singing using Convex AI singer
      const result = await generateSinging({
        lyrics: song.lyrics,
        voiceStyle: song.voiceStyle,
        mood: song.mood || "happy",
        pitchAdjustment: song.pitch || 0,
        includeMusic: true,
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to generate song');
      }

      // Update the song with the generated audio
      const audioDataUrl = `data:audio/wav;base64,${result.audio}`;
      await updateSong({
        id: song._id,
        generatedSongUrl: audioDataUrl,
      });
      
      Alert.alert("🎵 Success!", `Song generated successfully!\nDuration: ${result.duration_seconds?.toFixed(1)}s\nMethod: ${result.synthesis_method}`);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate song');
      Alert.alert("Error", err instanceof Error ? err.message : 'Failed to generate song');
    } finally {
      setIsGenerating(false);
    }
  };

  const regenerateSong = async () => {
    if (!song) return;
    
    // Show confirmation dialog
    Alert.alert(
      "Regenerate Song",
      hasUnsavedChanges 
        ? "This will save your changes and create a new version of your song. Continue?"
        : "This will create a new version of your song with the current lyrics and settings. Continue?",
      [
        {
          text: "Cancel",
          style: "cancel"
        },
        {
          text: "Regenerate",
          style: "destructive",
          onPress: async () => {
            setIsGenerating(true);
            setError(null);
            
            try {
              // First save any pending changes
              await saveChanges();
              await saveSettings(editedVoiceStyle, editedMood, pitch);
              
              // Generate singing using current edited values
              const result = await generateSinging({
                lyrics: editedLyrics,
                voiceStyle: editedVoiceStyle,
                mood: editedMood || "happy",
                pitchAdjustment: pitch,
                includeMusic: true,
              });

              if (!result.success) {
                throw new Error(result.error || 'Failed to regenerate song');
              }

              // Update the song with the new generated audio
              const audioDataUrl = `data:audio/wav;base64,${result.audio}`;
              await updateSong({
                id: song._id,
                generatedSongUrl: audioDataUrl,
              });
              
              setHasUnsavedChanges(false);
              Alert.alert("🎵 Success!", `Song regenerated successfully!\nDuration: ${result.duration_seconds?.toFixed(1)}s\nMethod: ${result.synthesis_method}`);
              
            } catch (err) {
              setError(err instanceof Error ? err.message : 'Failed to regenerate song');
              Alert.alert("Error", err instanceof Error ? err.message : 'Failed to regenerate song');
            } finally {
              setIsGenerating(false);
            }
          }
        }
      ]
    );
  };

  const saveChanges = async () => {
    if (!song) return;
    
    try {
      await updateSong({
        id: song._id,
        title: editedTitle,
        lyrics: editedLyrics,
      });
      Alert.alert("Success", "Changes saved!");
    } catch (err) {
      Alert.alert("Error", "Failed to save changes");
    }
  };

  const saveTitle = async () => {
    if (!song) return;
    try {
      await updateSong({
        id: song._id,
        title: editedTitle,
      });
      setIsEditingTitle(false);
    } catch (err) {
      Alert.alert("Error", "Failed to save title");
    }
  };

  const saveSettings = async (newVoiceStyle: string, newMood: string, newPitch: number) => {
    if (!song) return;
    try {
      await updateSong({
        id: song._id,
        voiceStyle: newVoiceStyle,
        mood: newMood,
        pitch: newPitch,
      });
      // Don't close modal automatically - let user see the regeneration
    } catch (err) {
      Alert.alert("Error", "Failed to save settings");
    }
  };

  if (!song) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading song...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header with buttons */}
      <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={async () => {
            // Auto-save any unsaved changes before leaving
            if (song && editedLyrics !== song.lyrics && editedLyrics.trim() !== song.lyrics.trim()) {
              try {
                await updateSong({ id: song._id, lyrics: editedLyrics });
                console.log("💾 Auto-saved lyrics on back button press");
              } catch (error) {
                console.error("Auto-save on back button failed:", error);
              }
            }
            navigation.goBack();
          }}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[
            styles.headerButton,
            hasUnsavedChanges && styles.headerButtonWarning
          ]}
          onPress={regenerateSong}
          disabled={isGenerating || isLoadingAudio}
        >
          {isGenerating || isLoadingAudio ? (
            <ActivityIndicator color="white" size="small" />
          ) : (
            <Text style={styles.headerButtonText}>🔄 Regenerate</Text>
          )}
        </TouchableOpacity>
        <View style={styles.headerCenter}>
          {isEditingTitle ? (
            <TextInput
              value={editedTitle}
              onChangeText={setEditedTitle}
              style={styles.editTitleInputCentered}
              placeholder="Song title..."
              placeholderTextColor="#999"
              onBlur={saveTitle}
              autoFocus
              textAlign="center"
            />
          ) : (
            <TouchableOpacity onPress={() => setIsEditingTitle(true)}>
              <Text style={styles.headerTitleCentered}>{editedTitle}</Text>
            </TouchableOpacity>
          )}

        </View>
        <TouchableOpacity 
          style={styles.headerButton}
          onPress={() => setShowSettings(true)}
        >
          <Text style={styles.headerButtonText}>⚙️</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.fullScreenLyricsArea}>
        {/* Song Metadata */}
        <View style={styles.metadataContainer}>
          {editedVoiceStyle && (
            <View style={styles.metadataTag}>
              <Text style={styles.metadataText}>{editedVoiceStyle} voice</Text>
            </View>
          )}
          {editedMood && (
            <View style={styles.metadataTag}>
              <Text style={styles.metadataText}>{editedMood}</Text>
            </View>
          )}
          {song.isHummingBased && (
            <View style={styles.metadataTag}>
              <Text style={styles.metadataText}>Humming-based</Text>
            </View>
          )}
          {hasUnsavedChanges && (
            <View style={styles.metadataTagWarning}>
              <Text style={styles.metadataTextWarning}>⚠️ Changes made - tap 🔄 to save & regenerate</Text>
            </View>
          )}
        </View>

        {/* Lyrics Section - Fullscreen, always editable */}
        <View style={styles.lyricsContainerFull}>
          <TextInput
            value={editedLyrics}
            onChangeText={handleLyricsChange}
            style={styles.editLyricsInputFull}
            placeholder="Write your lyrics here..."
            placeholderTextColor="#999"
            multiline
            textAlignVertical="top"
            autoFocus={false}
          />
        </View>

        {/* Audio Section */}
        {song.generatedSongUrl && (
          <View style={styles.audioContainer}>
            <Text style={styles.audioTitle}>Generated Song</Text>
            <View style={styles.audioControls}>
              <TouchableOpacity 
                style={styles.controlButton} 
                onPress={isPlaying ? stopAudio : playAudio}
                disabled={isLoadingAudio}
              >
                {isLoadingAudio ? (
                  <ActivityIndicator color="white" size="small" />
                ) : (
                  <Text style={styles.controlButtonText}>
                    {isPlaying ? "⏹️ Stop" : "▶️ Play Song"}
                  </Text>
                )}
              </TouchableOpacity>
            </View>
          </View>
        )}
      </View>

      {/* Settings Modal */}
      <Modal
        visible={showSettings}
        animationType="slide"
        presentationStyle="pageSheet"
        onRequestClose={() => setShowSettings(false)}
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Song Settings</Text>
            <TouchableOpacity onPress={() => setShowSettings(false)}>
              <Text style={styles.closeButton}>Done</Text>
            </TouchableOpacity>
          </View>
          <View style={styles.modalContent}>
            <Text style={styles.settingLabel}>Musical Style</Text>
            <View style={styles.optionButtons}>
              {['pop', 'ballad', 'jazz'].map((style) => (
                <TouchableOpacity
                  key={style}
                  style={[
                    styles.optionButton,
                    editedVoiceStyle === style && styles.optionButtonSelected
                  ]}
                  onPress={() => setEditedVoiceStyle(style)}
                >
                  <Text style={[
                    styles.optionButtonText,
                    editedVoiceStyle === style && styles.optionButtonTextSelected
                  ]}>
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            <Text style={styles.settingLabel}>Mood</Text>
            <View style={styles.optionButtons}>
              {['happy', 'sad', 'energetic'].map((moodOption) => (
                <TouchableOpacity
                  key={moodOption}
                  style={[
                    styles.optionButton,
                    editedMood === moodOption && styles.optionButtonSelected
                  ]}
                  onPress={() => setEditedMood(moodOption)}
                >
                  <Text style={[
                    styles.optionButtonText,
                    editedMood === moodOption && styles.optionButtonTextSelected
                  ]}>
                    {moodOption.charAt(0).toUpperCase() + moodOption.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
            
            <Text style={styles.settingLabel}>Voice Pitch: {pitch > 0 ? `+${pitch}` : pitch}</Text>
            <View style={styles.sliderContainer}>
              <Text style={styles.sliderLabel}>Lower</Text>
              <TouchableOpacity 
                style={styles.sliderTrack}
                onPress={(event) => {
                  const { locationX } = event.nativeEvent;
                  const trackWidth = event.target.measure((x, y, width) => {
                    const percentage = locationX / width;
                    const newPitch = Math.round((percentage * 24) - 12);
                    setPitch(Math.max(-12, Math.min(12, newPitch)));
                  });
                }}
              >
                <View 
                  style={[
                    styles.sliderThumb, 
                    { left: `${((pitch + 12) / 24) * 100}%` }
                  ]} 
                />
              </TouchableOpacity>
              <Text style={styles.sliderLabel}>Higher</Text>
            </View>
            <TouchableOpacity 
              style={styles.resetButton}
              onPress={() => setPitch(0)}
            >
              <Text style={styles.resetButtonText}>Reset to Normal</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.saveSettingsButton}
              onPress={() => saveSettings(editedVoiceStyle, editedMood, pitch)}
            >
              <Text style={styles.saveSettingsButtonText}>Save Settings</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    marginTop: 10,
    fontSize: 16,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 60,
    paddingBottom: 16,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    minWidth: 80,
    alignItems: 'center',
  },
  headerButtonWarning: {
    backgroundColor: '#FF9500',
  },
  backButton: {
    backgroundColor: 'transparent',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    minWidth: 40,
    alignItems: 'center',
  },
  backButtonText: {
    color: '#007AFF',
    fontSize: 24,
    fontWeight: '600',
  },
  headerButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    flex: 1,
    textAlign: 'center',
  },
  headerTitleCentered: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    textAlign: 'center',
  },
  editTitleInputCentered: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    textAlign: 'center',
    padding: 0,
    margin: 0,
    borderWidth: 0,
    borderRadius: 0,
    minWidth: 200,
  },
  fullScreenLyricsArea: {
    flex: 1,
    flexDirection: 'column',
    padding: 0,
    margin: 0,
    backgroundColor: '#f8f9fa',
  },
  metadataContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
    justifyContent: 'center',
  },
  metadataTag: {
    backgroundColor: '#e3f2fd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  metadataText: {
    fontSize: 12,
    color: '#1976d2',
    fontWeight: '500',
  },
  metadataTagWarning: {
    backgroundColor: '#fff3cd',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  metadataTextWarning: {
    fontSize: 12,
    color: '#856404',
    fontWeight: '500',
  },
  lyricsContainerFull: {
    flex: 1,
    margin: 0,
    padding: 0,
    backgroundColor: 'white',
    borderRadius: 0,
    justifyContent: 'flex-start',
  },
  editLyricsInputFull: {
    flex: 1,
    fontSize: 20,
    padding: 24,
    backgroundColor: 'white',
    color: '#1a1a1a',
    textAlignVertical: 'top',
    borderWidth: 0,
    borderRadius: 0,
    minHeight: height * 0.7,
  },
  lyricsTextFull: {
    fontSize: 20,
    color: '#1a1a1a',
    padding: 24,
    lineHeight: 32,
    minHeight: height * 0.7,
  },
  audioContainer: {
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  audioTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 16,
  },
  audioControls: {
    alignItems: 'center',
  },
  controlButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  controlButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
    padding: 20,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  closeButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '600',
  },
  modalContent: {
    marginTop: 20,
  },
  settingLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 10,
  },
  optionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    marginBottom: 20,
  },
  optionButton: {
    backgroundColor: '#e0e0e0',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 20,
    marginVertical: 5,
    minWidth: '45%', // Adjust as needed for spacing
  },
  optionButtonSelected: {
    backgroundColor: '#007AFF',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  optionButtonText: {
    fontSize: 16,
    color: '#333',
    fontWeight: '500',
  },
  optionButtonTextSelected: {
    color: 'white',
  },
  saveSettingsButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    paddingHorizontal: 30,
    borderRadius: 10,
    alignItems: 'center',
  },
  saveSettingsButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  autoSaveIndicator: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '500',
    marginTop: 2,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
    paddingHorizontal: 10,
  },
  sliderLabel: {
    fontSize: 14,
    color: '#666',
    marginHorizontal: 10,
  },
  sliderTrack: {
    flex: 1,
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    position: 'relative',
  },
  sliderThumb: {
    position: 'absolute',
    width: 20,
    height: 20,
    backgroundColor: '#007AFF',
    borderRadius: 10,
    top: -8,
    marginLeft: -10,
  },
  resetButton: {
    backgroundColor: '#f0f0f0',
    paddingVertical: 10,
    paddingHorizontal: 20,
    borderRadius: 8,
    alignItems: 'center',
    marginBottom: 20,
  },
  resetButtonText: {
    color: '#666',
    fontSize: 14,
    fontWeight: '500',
  },
});

export default SongDetailsScreen; 