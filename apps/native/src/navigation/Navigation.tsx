import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import CreateNoteScreen from "../screens/CreateNoteScreen";
import InsideNoteScreen from "../screens/InsideNoteScreen";
import LoginScreen from "../screens/LoginScreen";
import NotesDashboardScreen from "../screens/NotesDashboardScreen";
import SongsDashboardScreen from "../screens/SongsDashboardScreen";
import SongDetailsScreen from "../screens/SongDetailsScreen";
import CreateSongScreen from "../screens/CreateSongScreen";

// Define the stack param list for type safety
export type SongsStackParamList = {
  LoginScreen: undefined;
  SongsDashboardScreen: undefined;
  SongDetailsScreen: { songId: string } | undefined;
  CreateSongScreen: undefined;
};

const Stack = createNativeStackNavigator<SongsStackParamList>();

const Navigation = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        id={undefined}
        initialRouteName="SongsDashboardScreen"
        screenOptions={{ headerShown: false }}
      >
        <Stack.Screen name="LoginScreen" component={LoginScreen} />
        <Stack.Screen name="SongsDashboardScreen" component={SongsDashboardScreen} />
        <Stack.Screen name="SongDetailsScreen" component={SongDetailsScreen} />
        <Stack.Screen name="CreateSongScreen" component={CreateSongScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default Navigation;
