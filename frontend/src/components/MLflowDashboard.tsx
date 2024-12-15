import React, { useState, useEffect } from 'react';
import {
  Button,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
} from '@mui/material';
import axios from 'axios';

const API_URL = 'http://localhost:8000';

interface ModelInfo {
  run_id: string;
  start_time: number;
  metrics: Record<string, number>;
  parameters: Record<string, string>;
}

interface Recommendation {
  content_id: string;
  title: string;
  predicted_rating: number;
  confidence?: number;
}

const MLflowDashboard: React.FC = () => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch models on component mount
  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API_URL}/models`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setModels(response.data);
    } catch (err) {
      setError('Failed to fetch models');
      console.error(err);
    }
  };

  const trainModel = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.post(
        `${API_URL}/train`,
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      await fetchModels();
    } catch (err) {
      setError('Failed to train model');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const loadModel = async (runId: string) => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(
        `${API_URL}/models/${runId}/load`,
        {},
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        }
      );
      // Fetch recommendations after loading model
      const recsResponse = await axios.get(`${API_URL}/recommendations`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      setRecommendations(recsResponse.data);
    } catch (err) {
      setError('Failed to load model');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              MLflow Model Management
            </Typography>
            <Button
              variant="contained"
              color="primary"
              onClick={trainModel}
              disabled={loading}
            >
              {loading ? <CircularProgress size={24} /> : 'Train New Model'}
            </Button>
            {error && (
              <Typography color="error" style={{ marginTop: 16 }}>
                {error}
              </Typography>
            )}
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Available Models
            </Typography>
            <List>
              {models.map((model) => (
                <ListItem
                  key={model.run_id}
                  button
                  onClick={() => loadModel(model.run_id)}
                >
                  <ListItemText
                    primary={`Run ID: ${model.run_id}`}
                    secondary={
                      <>
                        <Typography component="span" variant="body2">
                          Training Size: {model.metrics.training_size}
                          <br />
                          Users: {model.metrics.n_users}
                          <br />
                          Movies: {model.metrics.n_movies}
                        </Typography>
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>

      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recommendations
            </Typography>
            <List>
              {recommendations.map((rec) => (
                <ListItem key={rec.content_id}>
                  <ListItemText
                    primary={rec.title}
                    secondary={`Predicted Rating: ${rec.predicted_rating}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default MLflowDashboard;
