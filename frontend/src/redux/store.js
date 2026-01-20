import { configureStore } from '@reduxjs/toolkit';
import interactionReducer from './slices/interactionSlide';

export const store = configureStore({
  reducer: {
    interaction: interactionReducer,
  },
});