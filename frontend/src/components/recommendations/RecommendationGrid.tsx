import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Card,
  CardContent,
  CardMedia,
  Typography,
  Rating,
  Box,
  CircularProgress,
  Alert,
} from '@mui/material';
import { AppDispatch, RootState } from '../../store/store';
import {
  fetchRecommendations,
  submitRating,
} from '../../store/slices/recommendationSlice';

const RecommendationGrid: React.FC = () => {
  const dispatch = useDispatch<AppDispatch>();
  const { recommendations, loading, error } = useSelector(
    (state: RootState) => state.recommendations
  );

  useEffect(() => {
    dispatch(fetchRecommendations(10));
  }, [dispatch]);

  const handleRatingChange = async (contentId: string, newValue: number | null) => {
    if (newValue !== null) {
      await dispatch(submitRating({ contentId, rating: newValue }));
      // Refresh recommendations after rating
      dispatch(fetchRecommendations(10));
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Grid container spacing={3} sx={{ p: 3 }}>
      {recommendations.map((content) => (
        <Grid item xs={12} sm={6} md={4} lg={3} key={content.content_id}>
          <Card
            sx={{
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              '&:hover': {
                transform: 'scale(1.02)',
                transition: 'transform 0.2s ease-in-out',
              },
            }}
          >
            <CardMedia
              component="img"
              height="200"
              image={`https://picsum.photos/seed/${content.content_id}/300/200`}
              alt={content.title}
            />
            <CardContent sx={{ flexGrow: 1 }}>
              <Typography gutterBottom variant="h6" component="div">
                {content.title}
              </Typography>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  mt: 2,
                }}
              >
                <Typography variant="body2" color="text.secondary">
                  Predicted Rating:
                </Typography>
                <Rating
                  value={content.predicted_rating}
                  precision={0.5}
                  onChange={(_, newValue) =>
                    handleRatingChange(content.content_id, newValue)
                  }
                />
              </Box>
              {content.confidence && (
                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mt: 1 }}
                >
                  Confidence: {(content.confidence * 100).toFixed(1)}%
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default RecommendationGrid;
