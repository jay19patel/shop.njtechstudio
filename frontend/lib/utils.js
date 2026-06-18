import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Merges class names safely, combining tailwind classes.
 * @param  {...any} inputs 
 * @returns {string}
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}
