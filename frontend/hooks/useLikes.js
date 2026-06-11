import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const useLikes = () => {
  const { user, isAuthenticated } = useAuth();
  const [likes, setLikes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [likedProducts, setLikedProducts] = useState(new Set());

  // Toggle like for a product
  const toggleLike = useCallback(async (productId) => {
    if (!isAuthenticated) {
      setError('You must be logged in to like products');
      return { success: false, liked: null };
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/likes/toggle-like/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({ product_id: productId }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to toggle like');
      }

      const data = await response.json();

      // Update liked products set
      setLikedProducts(prev => {
        const newSet = new Set(prev);
        if (data.liked) {
          newSet.add(productId);
        } else {
          newSet.delete(productId);
        }
        return newSet;
      });

      setError(null);
      return { success: true, liked: data.liked };
    } catch (err) {
      const errorMsg = err.message || 'Failed to toggle like';
      setError(errorMsg);
      return { success: false, liked: null };
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Check if a product is liked
  const isLiked = useCallback(async (productId) => {
    if (!isAuthenticated) return false;

    // Check in local state first
    if (likedProducts.has(productId)) return true;

    try {
      const response = await fetch(
        `${API_BASE}/api/likes/is-liked/?product_id=${productId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );

      if (!response.ok) throw new Error('Failed to check like status');

      const data = await response.json();

      if (data.is_liked) {
        setLikedProducts(prev => new Set(prev).add(productId));
      }

      return data.is_liked;
    } catch (err) {
      console.error('Error checking like status:', err);
      return false;
    }
  }, [isAuthenticated, likedProducts]);

  // Get user's liked products
  const getMyLikes = useCallback(async () => {
    if (!isAuthenticated) {
      setLikes([]);
      return [];
    }

    try {
      setLoading(true);
      const response = await fetch(`${API_BASE}/api/likes/my-likes/`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch likes');

      const data = await response.json();
      setLikes(data);

      // Update liked products set
      setLikedProducts(new Set(data.map(like => like.product_id)));

      setError(null);
      return data;
    } catch (err) {
      const errorMsg = err.message || 'Failed to fetch likes';
      setError(errorMsg);
      return [];
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  // Get likes count for a product
  const getLikesCount = useCallback(async (productId) => {
    try {
      const response = await fetch(
        `${API_BASE}/api/likes/is-liked/?product_id=${productId}`
      );

      if (!response.ok) throw new Error('Failed to get likes count');

      const data = await response.json();
      return data.likes_count || 0;
    } catch (err) {
      console.error('Error getting likes count:', err);
      return 0;
    }
  }, []);

  // Fetch my likes on auth change
  useEffect(() => {
    if (isAuthenticated && user) {
      getMyLikes();
    }
  }, [isAuthenticated, user]);

  return {
    likes,
    loading,
    error,
    toggleLike,
    isLiked,
    getMyLikes,
    getLikesCount,
    likedProducts,
  };
};
