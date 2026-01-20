import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  formData: {
    hcpName: '',
    date: '',
    time: '',
    interactionType: 'Meeting',
    topics: '',
    materialsDistributed: '',
    outcomes: 'Neutral',
    followUp: '',
    summary: '',
  },
  chatMessages: [],
  loading: false,
};

const interactionSlice = createSlice({
  name: 'interaction',
  initialState,
  reducers: {
    updateForm: (state, action) => {
      state.formData = { ...state.formData, ...action.payload };
    },
    addChatMessage: (state, action) => {
      state.chatMessages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
  },
});

export const { updateForm, addChatMessage, setLoading } = interactionSlice.actions;
export default interactionSlice.reducer;