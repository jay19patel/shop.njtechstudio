import React, { useState, useEffect } from 'react';
import { Heart } from 'lucide-react';
import { useLikes } from '../../hooks/useLikes';
import { useAuth } from '../../context/AuthContext';

export default function LikeButton({
  productId,
  variant = 'icon',
  size = 'md',
  showCount = false,
  className = '',
  onLikeChange = null,
}) {
  const { isAuthenticated } = useAuth();
  const { toggleLike, likedProducts, loading } = useLikes();
  const [isLiked, setIsLiked] = useState(false);
  const [count, setCount] = useState(0);

  useEffect(() => {
    setIsLiked(likedProducts.has(productId));
  }, [likedProducts, productId]);

  const handleClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    if (!isAuthenticated) {
      alert('Please log in to like products');
      return;
    }

    const result = await toggleLike(productId);

    if (result.success) {
      setIsLiked(result.liked);
      if (onLikeChange) {
        onLikeChange(result.liked);
      }
    }
  };

  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
  };

  if (variant === 'icon') {
    return (
      <button
        onClick={handleClick}
        disabled={loading}
        className={`transition-all duration-200 ${loading ? 'opacity-50 cursor-not-allowed' : ''} ${className}`}
        title={isLiked ? 'Unlike' : 'Like'}
      >
        <Heart
          className={`${sizes[size]} transition-all duration-200 ${
            isLiked
              ? 'fill-red-600 text-red-600 scale-110'
              : 'text-slate-400 hover:text-slate-600'
          }`}
        />
      </button>
    );
  }

  if (variant === 'button') {
    return (
      <button
        onClick={handleClick}
        disabled={loading}
        className={`
          flex items-center gap-2 px-3 py-1.5 text-xs font-semibold
          rounded-lg transition-all duration-200
          ${
            isLiked
              ? 'bg-red-50 text-red-700 border border-red-200 hover:bg-red-100'
              : 'bg-slate-50 text-slate-600 border border-slate-200 hover:bg-slate-100'
          }
          ${loading ? 'opacity-50 cursor-not-allowed' : ''}
          ${className}
        `}
      >
        <Heart className={`${sizes[size]} ${isLiked ? 'fill-current' : ''}`} />
        {showCount && <span>{count}</span>}
      </button>
    );
  }

  return null;
}
