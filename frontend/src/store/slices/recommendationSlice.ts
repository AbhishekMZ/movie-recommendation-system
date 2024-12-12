import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

interface Content {
  content_id: string;
  title: string;
  predicted_rating: number;
  confidence: number;
}

interface RecommendationState {
  recommendations: Content[];
  loading: boolean;
  error: string | null;
}

const initialState: RecommendationState = {
  recommendations: [],
  loading: false,
  error: null,
};

export const fetchRecommendations = createAsyncThunk(
  'recommendations/fetch',
  async (limit: number = 10, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as { auth: { token: string } };
      const response = await axios.get(`http://localhost:8000/recommendations/?limit=${limit}`, {
        headers: { Authorization: `Bearer ${auth.token}` }
      });
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch recommendations');
    }
  }
);

export const submitRating = createAsyncThunk(
  'recommendations/submitRating',
  async ({ contentId, rating }: { contentId: string; rating: number }, { getState, rejectWithValue }) => {
    try {
      const { auth } = getState() as { auth: { token: string } };
      const response = await axios.post(
        'http://localhost:8000/ratings/',
        { content_id: contentId, rating },
        { headers: { Authorization: `Bearer ${auth.token}` } }
      );
      return response.data;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to submit rating');
    }
  }
);

const recommendationSlice = createSlice({
  name: 'recommendations',
  initialState,
  reducers: {
    clearRecommendations: (state) => {
      state.recommendations = [];
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchRecommendations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchRecommendations.fulfilled, (state, action) => {
        state.loading = false;
        state.recommendations = action.payload;
      })
      .addCase(fetchRecommendations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(submitRating.rejected, (state, action) => {
        state.error = action.payload as string;
      });
  },
});

export const { clearRecommendations } = recommendationSlice.actions;
export default recommendationSlice.reducer;
