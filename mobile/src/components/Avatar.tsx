/**
 * Photorealistic portraits for the chat companions.
 *
 * Replaced the old SVG illustrations with high-quality generated faces
 * to match the premium "cosmic" aesthetic of the app.
 * Fixed the duplicate faces (now exactly 12 unique faces).
 */

import { Image, View } from 'react-native';

export type Persona = {
  id: string;
  name: string;
  image: any;
};

export const PERSONAS: Persona[] = [
  { id: 'aarav', name: 'Aarav', image: require('../../assets/faces/aarav.jpg') },
  { id: 'meera', name: 'Meera', image: require('../../assets/faces/meera.jpg') },
  { id: 'maya', name: 'Maya', image: require('../../assets/faces/maya.jpg') },
  { id: 'emma', name: 'Emma', image: require('../../assets/faces/emma.jpg') },
  { id: 'grace', name: 'Grace', image: require('../../assets/faces/grace.jpg') },
  { id: 'yuna', name: 'Yuna', image: require('../../assets/faces/yuna.jpg') },
  { id: 'mateo', name: 'Mateo', image: require('../../assets/faces/mateo.jpg') },
  { id: 'omar', name: 'Omar', image: require('../../assets/faces/omar.jpg') },
  { id: 'vikram', name: 'Vikram', image: require('../../assets/faces/vikram.jpg') },
  { id: 'kenji', name: 'Kenji', image: require('../../assets/faces/kenji.jpg') },
  { id: 'leo', name: 'Leo', image: require('../../assets/faces/leo.jpg') },
  { id: 'marcus', name: 'Marcus', image: require('../../assets/faces/marcus.jpg') },
];

export function Portrait({ person, size = 84 }: { person: Persona; size?: number }) {
  if (!person) return null;
  
  return (
    <View style={{ width: size, height: size, borderRadius: size / 2, overflow: 'hidden' }}>
      <Image
        source={person.image}
        style={{ width: '100%', height: '100%', resizeMode: 'cover' }}
      />
    </View>
  );
}
