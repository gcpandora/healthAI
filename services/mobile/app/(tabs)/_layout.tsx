import { Tabs } from 'expo-router';
import { Text, ColorValue } from 'react-native';

function TabIcon({ symbol, color }: { symbol: string; color: ColorValue }) {
  return <Text style={{ color, fontSize: 22, lineHeight: 26 }}>{symbol}</Text>;
}

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: '#1a73e8',
        tabBarInactiveTintColor: '#999',
        tabBarStyle: { paddingBottom: 4 },
        headerShown: false,
      }}
    >
      <Tabs.Screen
        name="index"
        options={{
          title: 'Flux',
          tabBarIcon: ({ color }) => <TabIcon symbol="⊞" color={color} />,
        }}
      />
      <Tabs.Screen
        name="create"
        options={{
          title: 'Créer',
          tabBarIcon: ({ color }) => <TabIcon symbol="+" color={color} />,
        }}
      />
      <Tabs.Screen
        name="profile"
        options={{
          title: 'Profil',
          tabBarIcon: ({ color }) => <TabIcon symbol="◉" color={color} />,
        }}
      />
    </Tabs>
  );
}
