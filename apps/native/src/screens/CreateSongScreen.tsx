import React, { useState } from "react";
import { 
  View, 
  Text, 
  TextInput, 
  TouchableOpacity, 
  ActivityIndicator, 
  Alert, 
  ScrollView, 
  Modal,
  StyleSheet,
  Dimensions
} from "react-native";
import { useMutation, useAction } from "convex/react";
import { api } from "@packages/backend/convex/_generated/api";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { SongsStackParamList } from "../navigation/Navigation";

const { width, height } = Dimensions.get('window');

const CreateSongScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<SongsStackParamList>>();
  const createSongWithAI = useAction(api.songs.createSongWithAI);
  
  // Main form state
  const [title, setTitle] = useState("");
  const [lyrics, setLyrics] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [autoSaveTimer, setAutoSaveTimer] = useState<NodeJS.Timeout | null>(null);
  const [lastSavedTitle, setLastSavedTitle] = useState("");
  const [lastSavedLyrics, setLastSavedLyrics] = useState("");
  const [isAutoSaving, setIsAutoSaving] = useState(false);
  
  // Settings modal state
  const [showSettings, setShowSettings] = useState(false);
  const [voiceStyle, setVoiceStyle] = useState("pop");
  const [mood, setMood] = useState("happy");
  const [includeMusic, setIncludeMusic] = useState(true);
  const [useGeminiTTS, setUseGeminiTTS] = useState(true);
  const [pitch, setPitch] = useState(0);

  // Auto-save functionality
  const saveToLocalStorage = async (title: string, lyrics: string) => {
    try {
      const saveData = {
        title,
        lyrics,
        voiceStyle,
        mood,
        includeMusic,
        useGeminiTTS,
        pitch,
        timestamp: Date.now()
      };
      // In a real app, you'd use AsyncStorage here
      // For now, we'll just track what was saved
      setLastSavedTitle(title);
      setLastSavedLyrics(lyrics);
      console.log("💾 Auto-saved:", { title, lyrics });
    } catch (error) {
      console.error("Auto-save failed:", error);
    }
  };

  const scheduleAutoSave = React.useCallback((title: string, lyrics: string) => {
    // Clear existing timer
    if (autoSaveTimer) {
      clearTimeout(autoSaveTimer);
    }
    
    // Show auto-saving indicator
    setIsAutoSaving(true);
    
    // Set new timer (save after 2 seconds of no typing)
    const timer = setTimeout(() => {
      saveToLocalStorage(title, lyrics);
      setIsAutoSaving(false);
    }, 2000);
    
    setAutoSaveTimer(timer);
  }, [autoSaveTimer]);

  const handleTitleChange = React.useCallback((newTitle: string) => {
    setTitle(newTitle);
    scheduleAutoSave(newTitle, lyrics);
  }, [scheduleAutoSave, lyrics]);

  const handleLyricsChange = React.useCallback((newLyrics: string) => {
    setLyrics(newLyrics);
    scheduleAutoSave(title, newLyrics);
  }, [scheduleAutoSave, title]);

  // Auto-save when leaving screen and cleanup timer on unmount
  React.useEffect(() => {
    return () => {
      // Auto-save any unsaved changes when leaving the screen
      if (title.trim() || lyrics.trim()) {
        saveToLocalStorage(title, lyrics);
        console.log("💾 Auto-saved draft on screen exit");
      }
      
      // Cleanup timer
      if (autoSaveTimer) {
        clearTimeout(autoSaveTimer);
      }
    };
  }, [autoSaveTimer, title, lyrics]);

  const handleCreate = async () => {
    if (!title.trim() || !lyrics.trim()) {
      Alert.alert("Error", "Please fill in both title and lyrics");
      return;
    }
    
    setIsGenerating(true);
    try {
      // Create song with AI singing using Convex action
      const result = await createSongWithAI({
        title,
        lyrics,
        voiceStyle,
        mood,
        includeMusic,
      });

      if (!result.success) {
        throw new Error(result.error || 'Failed to generate singing audio');
      }

      Alert.alert(
        "Success!", 
        `Song "${title}" created successfully!\nDuration: ${result.duration?.toFixed(1)}s\nMethod: ${result.synthesisMethod}`,
        [
          {
            text: "View Song",
            onPress: () => navigation.navigate("SongDetailsScreen", { songId: result.songId })
          },
          {
            text: "Create Another",
            onPress: () => {
              setTitle("");
              setLyrics("");
            }
          }
        ]
      );
      
    } catch (error) {
      console.error("Song creation failed:", error);
      Alert.alert("Error", `Failed to create song: ${error}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const SettingsModal = () => (
    <Modal
      visible={showSettings}
      animationType="slide"
      presentationStyle="pageSheet"
    >
      <View style={styles.modalContainer}>
        <View style={styles.modalHeader}>
          <Text style={styles.modalTitle}>Song Settings</Text>
          <TouchableOpacity onPress={() => setShowSettings(false)}>
            <Text style={styles.closeButton}>Done</Text>
          </TouchableOpacity>
        </View>
        
        <ScrollView style={styles.modalContent}>
          <View style={styles.settingGroup}>
            <Text style={styles.settingLabel}>Musical Style</Text>
            <View style={styles.optionButtons}>
              {['pop', 'ballad', 'jazz'].map((style) => (
                <TouchableOpacity
                  key={style}
                  style={[
                    styles.optionButton,
                    voiceStyle === style && styles.optionButtonSelected
                  ]}
                  onPress={() => setVoiceStyle(style)}
                >
                  <Text style={[
                    styles.optionButtonText,
                    voiceStyle === style && styles.optionButtonTextSelected
                  ]}>
                    {style.charAt(0).toUpperCase() + style.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.settingGroup}>
            <Text style={styles.settingLabel}>Mood</Text>
            <View style={styles.optionButtons}>
              {['happy', 'sad', 'energetic'].map((moodOption) => (
                <TouchableOpacity
                  key={moodOption}
                  style={[
                    styles.optionButton,
                    mood === moodOption && styles.optionButtonSelected
                  ]}
                  onPress={() => setMood(moodOption)}
                >
                  <Text style={[
                    styles.optionButtonText,
                    mood === moodOption && styles.optionButtonTextSelected
                  ]}>
                    {moodOption.charAt(0).toUpperCase() + moodOption.slice(1)}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>

          <View style={styles.settingGroup}>
            <TouchableOpacity 
              style={styles.checkboxRow}
              onPress={() => setUseGeminiTTS(!useGeminiTTS)}
            >
              <View style={[styles.checkbox, useGeminiTTS && styles.checkboxChecked]}>
                {useGeminiTTS && <Text style={styles.checkmark}>✓</Text>}
              </View>
              <Text style={styles.checkboxLabel}>Use Gemini TTS for enhanced vocals</Text>
            </TouchableOpacity>
          </View>

          {useGeminiTTS && (
            <View style={styles.settingGroup}>
              <Text style={styles.settingLabel}>Voice Pitch: {pitch > 0 ? `+${pitch}` : pitch}</Text>
              <View style={styles.sliderContainer}>
                <Text style={styles.sliderLabel}>Lower</Text>
                <View style={styles.sliderTrack}>
                  <View 
                    style={[
                      styles.sliderThumb, 
                      { left: `${((pitch + 12) / 24) * 100}%` }
                    ]} 
                  />
                </View>
                <Text style={styles.sliderLabel}>Higher</Text>
              </View>
              <TouchableOpacity 
                style={styles.resetButton}
                onPress={() => setPitch(0)}
              >
                <Text style={styles.resetButtonText}>Reset to Normal</Text>
              </TouchableOpacity>
            </View>
          )}

          <View style={styles.settingGroup}>
            <Text style={styles.settingLabel}>Audio Options</Text>
            <TouchableOpacity 
              style={styles.checkboxRow}
              onPress={() => setIncludeMusic(!includeMusic)}
            >
              <View style={[styles.checkbox, includeMusic && styles.checkboxChecked]}>
                {includeMusic && <Text style={styles.checkmark}>✓</Text>}
              </View>
              <Text style={styles.checkboxLabel}>Include instrumental accompaniment</Text>
            </TouchableOpacity>
            {!includeMusic && (
              <Text style={styles.settingNote}>🎤 Vocals only - perfect for hearing the singing voice clearly</Text>
            )}
            {includeMusic && (
              <Text style={styles.settingNote}>🎵 Vocals + background music</Text>
            )}
          </View>
        </ScrollView>
      </View>
    </Modal>
  );

  return (
    <View style={styles.container}>
      {/* Header with buttons */}
            <View style={styles.header}>
        <TouchableOpacity 
          style={styles.backButton}
          onPress={() => {
            // Auto-save any unsaved changes before leaving
            if (title.trim() || lyrics.trim()) {
              saveToLocalStorage(title, lyrics);
              console.log("💾 Auto-saved draft on back button press");
            }
            navigation.goBack();
          }}
        >
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[
            styles.headerButton, 
            (!title.trim() || !lyrics.trim() || isGenerating) && styles.headerButtonDisabled
          ]} 
          onPress={handleCreate} 
          disabled={!title.trim() || !lyrics.trim() || isGenerating}
        >
          {isGenerating ? (
            <ActivityIndicator color="white" size="small" />
          ) : (
            <Text style={styles.headerButtonText}>🎵 Generate</Text>
          )}
        </TouchableOpacity>
        
        <View style={styles.headerCenter}>
          <Text style={styles.headerTitle}>Create New Song</Text>
          {isAutoSaving && (
            <Text style={styles.autoSaveIndicator}>💾 Auto-saving...</Text>
          )}
        </View>
        
        <View style={styles.headerRight}>
          <TouchableOpacity 
            style={styles.musicToggleButton}
            onPress={() => setIncludeMusic(!includeMusic)}
          >
            <Text style={styles.musicToggleText}>
              {includeMusic ? "🎵" : "🎤"}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity 
            style={styles.headerButton}
            onPress={() => setShowSettings(true)}
          >
            <Text style={styles.headerButtonText}>⚙️</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Main Content */}
      <View style={styles.content}>
        {/* Title Input - Compact */}
        <View style={styles.titleContainer}>
          <TextInput
            value={title}
            onChangeText={handleTitleChange}
            placeholder="Song title..."
            style={styles.titleInput}
            placeholderTextColor="#999"
          />
        </View>

        {/* Lyrics Input - Takes up most of the screen */}
        <View style={styles.lyricsContainer}>
          <TextInput
            value={lyrics}
            onChangeText={handleLyricsChange}
            placeholder="Write your lyrics here...\n\nStart with a verse, then a chorus...\n\nLet your creativity flow!"
            multiline
            style={styles.lyricsInput}
            placeholderTextColor="#999"
            textAlignVertical="top"
            autoFocus={true}
          />
        </View>

        {/* Helper text */}
        {(!title.trim() || !lyrics.trim()) && (
          <Text style={styles.helperText}>
            Add a title and lyrics above, then tap "Generate" to create your AI song
          </Text>
        )}
      </View>

      <SettingsModal />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
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
  headerButtonDisabled: {
    backgroundColor: '#ccc',
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
  headerRight: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  musicToggleButton: {
    backgroundColor: '#34C759',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    minWidth: 40,
    alignItems: 'center',
  },
  musicToggleText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  headerCenter: {
    flex: 1,
    alignItems: 'center',
  },
  autoSaveIndicator: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '500',
    marginTop: 2,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    flex: 1,
    textAlign: 'center',
  },
  content: {
    flex: 1,
    padding: 16,
  },
  titleContainer: {
    marginBottom: 16,
  },
  titleInput: {
    borderWidth: 1,
    borderColor: '#d0d5dd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: 'white',
    textAlign: 'center',
  },
  lyricsContainer: {
    flex: 1,
    marginBottom: 16,
  },
  lyricsInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#d0d5dd',
    borderRadius: 12,
    padding: 20,
    fontSize: 18,
    backgroundColor: 'white',
    lineHeight: 28,
    textAlignVertical: 'top',
  },
  helperText: {
    textAlign: 'center',
    color: '#666',
    fontSize: 14,
    fontStyle: 'italic',
  },
  // Modal styles
  modalContainer: {
    flex: 1,
    backgroundColor: 'white',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  closeButton: {
    fontSize: 16,
    color: '#007AFF',
    fontWeight: '500',
  },
  modalContent: {
    flex: 1,
    padding: 20,
  },
  settingGroup: {
    marginBottom: 24,
  },
  settingLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  picker: {
    borderWidth: 1,
    borderColor: '#d0d5dd',
    borderRadius: 8,
    backgroundColor: 'white',
  },
  optionButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  optionButton: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderWidth: 1,
    borderColor: '#d0d5dd',
    borderRadius: 8,
    backgroundColor: 'white',
    minWidth: 80,
    alignItems: 'center',
  },
  optionButtonSelected: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  optionButtonText: {
    fontSize: 14,
    color: '#1a1a1a',
    fontWeight: '500',
  },
  optionButtonTextSelected: {
    color: 'white',
  },
  checkboxRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  checkbox: {
    width: 20,
    height: 20,
    borderWidth: 2,
    borderColor: '#d0d5dd',
    borderRadius: 4,
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkboxChecked: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  checkmark: {
    color: 'white',
    fontSize: 12,
    fontWeight: 'bold',
  },
  checkboxLabel: {
    fontSize: 16,
    color: '#1a1a1a',
    flex: 1,
  },
  settingNote: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    marginTop: 8,
    marginLeft: 24,
  },
  sliderContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 8,
  },
  sliderLabel: {
    fontSize: 12,
    color: '#666',
    width: 50,
  },
  sliderTrack: {
    flex: 1,
    height: 4,
    backgroundColor: '#e9ecef',
    borderRadius: 2,
    marginHorizontal: 10,
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
    alignSelf: 'center',
    marginTop: 8,
    paddingVertical: 8,
    paddingHorizontal: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 6,
  },
  resetButtonText: {
    color: '#007AFF',
    fontSize: 14,
    fontWeight: '500',
  },
});

export default CreateSongScreen; 