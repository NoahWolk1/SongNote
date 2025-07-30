import React from "react";
import { View, Text, TouchableOpacity, FlatList, ActivityIndicator, Alert, StyleSheet } from "react-native";
import { useNavigation } from "@react-navigation/native";
import type { NativeStackNavigationProp } from "@react-navigation/native-stack";
import type { SongsStackParamList } from "../navigation/Navigation";
import { api } from "@packages/backend/convex/_generated/api";
import { useQuery, useMutation } from "convex/react";

const SongsDashboardScreen = () => {
  const navigation = useNavigation<NativeStackNavigationProp<SongsStackParamList>>();
  const songs = useQuery(api.songs.getSongs);
  const deleteSong = useMutation(api.songs.deleteSong);

  const handleDelete = (songId: string) => {
    Alert.alert(
      "Delete Song",
      "Are you sure you want to delete this song?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              await deleteSong({ songId: songId as any });
            } catch (err) {
              Alert.alert("Error", err instanceof Error ? err.message : "Failed to delete song");
            }
          },
        },
      ]
    );
  };

  if (songs === undefined) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" />
        <Text style={styles.loadingText}>Loading songs...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Your AI-Generated Songs</Text>
        <TouchableOpacity 
          style={styles.createButton}
          onPress={() => navigation.navigate("CreateSongScreen")}
        >
          <Text style={styles.createButtonText}>+ New Song</Text>
        </TouchableOpacity>
      </View>

      {/* Songs List */}
      <View style={styles.content}>
        {(!songs || songs.length === 0) ? (
          <View style={styles.emptyContainer}>
            <Text style={styles.emptyTitle}>No songs yet</Text>
            <Text style={styles.emptyText}>
              Create your first AI-generated song to get started!
            </Text>
            <TouchableOpacity 
              style={styles.emptyCreateButton}
              onPress={() => navigation.navigate("CreateSongScreen")}
            >
              <Text style={styles.emptyCreateButtonText}>Create Your First Song</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <FlatList
            data={songs}
            keyExtractor={item => item._id}
            renderItem={({ item }) => (
              <TouchableOpacity
                style={styles.songCard}
                onPress={() => navigation.navigate("SongDetailsScreen", { songId: item._id })}
              >
                <View style={styles.songInfo}>
                  <Text style={styles.songTitle}>{item.title}</Text>
                  <Text numberOfLines={2} style={styles.songLyrics}>{item.lyrics}</Text>
                  <View style={styles.songMetadata}>
                    {item.voiceStyle && (
                      <Text style={styles.metadataText}>{item.voiceStyle}</Text>
                    )}
                    {item.mood && (
                      <Text style={styles.metadataText}>• {item.mood}</Text>
                    )}
                    {item.generatedSongUrl && (
                      <Text style={styles.metadataText}>• 🎵 Ready</Text>
                    )}
                  </View>
                </View>
                <TouchableOpacity 
                  style={styles.deleteButton}
                  onPress={() => handleDelete(item._id)}
                >
                  <Text style={styles.deleteButtonText}>🗑️</Text>
                </TouchableOpacity>
              </TouchableOpacity>
            )}
            showsVerticalScrollIndicator={false}
          />
        )}
      </View>
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
    paddingHorizontal: 20,
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1a1a1a',
  },
  createButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
  },
  createButtonText: {
    color: 'white',
    fontSize: 14,
    fontWeight: '600',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  emptyContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 40,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  emptyText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  emptyCreateButton: {
    backgroundColor: '#007AFF',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
  },
  emptyCreateButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  songCard: {
    backgroundColor: 'white',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: 'row',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  songInfo: {
    flex: 1,
  },
  songTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  songLyrics: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 8,
  },
  songMetadata: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  metadataText: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '500',
    marginRight: 8,
  },
  deleteButton: {
    padding: 8,
  },
  deleteButtonText: {
    fontSize: 18,
  },
});

export default SongsDashboardScreen; 