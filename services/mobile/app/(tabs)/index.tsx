import { View, Text, StyleSheet } from 'react-native';

export default function FluxScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.placeholder}>Feed à venir</Text>
      <Text style={styles.hint}>Les publications apparaîtront ici.</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
  },
  placeholder: {
    fontSize: 22,
    fontWeight: '600',
    color: '#444',
  },
  hint: {
    fontSize: 14,
    color: '#999',
    marginTop: 8,
  },
});
