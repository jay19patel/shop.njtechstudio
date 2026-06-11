# Design System Implementation Guide

This document outlines the unified design system extracted from the Admin Dashboard and provides guidelines for implementing it across the entire application.

## Overview

The design system is the **SINGLE SOURCE OF TRUTH** for all visual and UI decisions across the application. Every page should follow these patterns to ensure consistency.

## Design Tokens

All design tokens are defined in `lib/designTokens.js`. This file contains:

- **Colors**: Primary, text, status colors, backgrounds, borders
- **Spacing**: XS to 4XL scales
- **Border Radius**: SM to XL with full circle option
- **Shadows**: None to XL intensity
- **Typography**: Page titles, section titles, labels, body text
- **Buttons**: Primary, secondary, ghost, pill variants
- **Inputs**: Base, large, search styles
- **Cards**: Base styles with padding options
- **Badges**: Success, info, warning, error, neutral, primary variants
- **Layouts**: Container, page, and grid layouts

### Usage Example

```javascript
import { colors, spacing, typography, buttons } from '@/lib/designTokens';

// In your component
<button className={buttons.primary}>Click Me</button>
<h2 className={typography.sectionTitle}>Section Title</h2>
```

## Reusable UI Components

Located in `components/ui/`, these are the building blocks for the design system:

### Button
```javascript
import { Button } from '@/components/ui';

<Button variant="primary" size="md">Save Changes</Button>
<Button variant="secondary" size="lg">Cancel</Button>
<Button variant="ghost">Link Button</Button>
<Button variant="danger" disabled>Delete</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'ghost' | 'danger'
- `size`: 'sm' | 'md' | 'lg' | 'pill'
- `disabled`: boolean
- `className`: additional Tailwind classes

### Card
```javascript
import { Card } from '@/components/ui';

<Card padding="md" hoverable>
  Content goes here
</Card>
```

**Props:**
- `padding`: 'sm' | 'md' | 'lg' | 'none'
- `hoverable`: boolean (adds hover effects)
- `className`: additional classes

### Input
```javascript
import { Input } from '@/components/ui';
import { Search } from 'lucide-react';

<Input 
  label="Email Address"
  placeholder="Enter your email"
  type="email"
  value={email}
  onChange={(e) => setEmail(e.target.value)}
  icon={Search}
  error={error && "Invalid email"}
/>
```

**Props:**
- `label`: string
- `placeholder`: string
- `type`: input type
- `value`: current value
- `onChange`: change handler
- `error`: error message (shows red border)
- `icon`: Lucide icon component
- `disabled`: boolean

### Textarea
```javascript
import { Textarea } from '@/components/ui';

<Textarea
  label="Message"
  placeholder="Enter your message"
  value={message}
  onChange={(e) => setMessage(e.target.value)}
  rows={5}
  error={error}
/>
```

### Badge
```javascript
import { Badge } from '@/components/ui';

<Badge variant="success">Delivered</Badge>
<Badge variant="warning">Pending</Badge>
<Badge variant="error">Cancelled</Badge>
<Badge variant="info" size="lg">Processing</Badge>
```

**Props:**
- `variant`: 'success' | 'info' | 'warning' | 'error' | 'neutral' | 'primary'
- `size`: 'sm' | 'md' | 'lg'

### PageHeader
```javascript
import { PageHeader } from '@/components/ui';
import { Button } from '@/components/ui';

<PageHeader
  title="Dashboard"
  subtitle="Admin"
  actions={
    <Button variant="primary">Add New</Button>
  }
/>
```

### SectionHeader
```javascript
import { SectionHeader } from '@/components/ui';

<SectionHeader
  title="Recent Orders"
  count={orders.length}
  action={<RefreshButton />}
/>
```

### Avatar
```javascript
import { Avatar } from '@/components/ui';

<Avatar 
  src={user.profileImage} 
  alt="User Avatar"
  size="md"
/>
```

**Props:**
- `src`: image URL
- `alt`: alt text
- `size`: 'sm' | 'md' | 'lg' | 'xl'

### EmptyState
```javascript
import { EmptyState } from '@/components/ui';
import { ShoppingBag } from 'lucide-react';

<EmptyState
  icon={ShoppingBag}
  title="No items found"
  description="Your cart is empty. Start shopping to add items."
  action={<Button>Browse Products</Button>}
/>
```

### LoadingSpinner
```javascript
import { LoadingSpinner } from '@/components/ui';

<LoadingSpinner size="md" text="Loading products..." />
<LoadingSpinner size="lg" fullScreen={true} />
```

## Likes Feature Integration

### Using the useLikes Hook

```javascript
import { useLikes } from '@/hooks/useLikes';

function ProductCard({ product }) {
  const { toggleLike, likedProducts } = useLikes();
  
  return (
    <div>
      <h2>{product.name}</h2>
      <LikeButton 
        productId={product.id}
        variant="icon"
        size="md"
      />
    </div>
  );
}
```

### Hook API

```javascript
const {
  likes,              // Array of liked products
  loading,            // Loading state
  error,              // Error message if any
  toggleLike,         // Function to toggle like (productId) => Promise
  isLiked,            // Function to check if liked
  getMyLikes,         // Function to fetch all likes
  getLikesCount,      // Function to get count for product
  likedProducts,      // Set of liked product IDs
} = useLikes();
```

### LikeButton Component

```javascript
import { LikeButton } from '@/components/ui';

// Icon variant (just the heart)
<LikeButton 
  productId={productId}
  variant="icon"
  size="md"
/>

// Button variant (with label and count)
<LikeButton 
  productId={productId}
  variant="button"
  showCount={true}
  onLikeChange={(isLiked) => console.log(isLiked)}
/>
```

## Admin Dashboard Design Patterns

The Admin Dashboard exemplifies the design system. Key patterns:

### Page Layout
```javascript
<div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
  <Navbar />
  <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
    <div className="flex flex-col gap-8">
      {/* Content */}
    </div>
  </main>
  <Footer />
</div>
```

### Stats Grid
```javascript
<div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3">
  {stats.map(stat => (
    <Card padding="md" key={stat.label}>
      <Icon className="w-4 h-4 text-slate-400" />
      <p className={typography.label}>{stat.label}</p>
      <p className={typography.pageTitle}>{stat.value}</p>
    </Card>
  ))}
</div>
```

### Tables
```javascript
<Card padding="none">
  <SectionHeader 
    title="Recent Orders"
    count={orders.length}
    action={<SearchInput />}
  />
  <div className="overflow-x-auto">
    <table className="w-full">
      {/* Table content */}
    </table>
  </div>
</Card>
```

## Responsive Behavior

All components follow the responsive patterns established in the Admin Dashboard:

- **Mobile First**: Default to mobile, enhance for larger screens
- **Breakpoints**: 
  - `sm:` for 640px and up
  - `lg:` for 1024px and up
  - `xl:` for 1280px and up

Example:
```javascript
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
  {/* Cards adjust based on screen size */}
</div>
```

## Colors & Status States

### Order Status Badges
```javascript
import { Badge } from '@/components/ui';

const statuses = {
  PENDING: <Badge variant="warning">Pending</Badge>,
  PROCESSING: <Badge variant="info">Processing</Badge>,
  SHIPPED: <Badge variant="info">Shipped</Badge>,
  DELIVERED: <Badge variant="success">Delivered</Badge>,
  CANCELLED: <Badge variant="error">Cancelled</Badge>,
};
```

### Payment Status
```javascript
const paymentStatuses = {
  PENDING: 'bg-orange-50 text-orange-700 border-orange-200',
  RECEIVED: 'bg-blue-50 text-blue-700 border-blue-200',
  VERIFIED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
  FAILED: 'bg-red-50 text-red-700 border-red-200',
};
```

## Typography Hierarchy

```javascript
// Page Title
<h1 className={typography.pageTitle}>Page Title</h1>

// Section Title
<h2 className={typography.sectionTitle}>Section Title</h2>

// Label
<label className={typography.label}>Label Text</label>

// Body
<p className={typography.body}>Regular paragraph text</p>

// Body Small
<p className={typography.bodySmall}>Smaller text</p>
```

## Updating Existing Pages

When refactoring a page to match the design system:

1. **Replace hardcoded styles** with component classes or design tokens
2. **Use reusable components** instead of inline code
3. **Follow the layout pattern**:
   - Min-height screen with flex column
   - Navbar at top
   - Main content area with max-width container
   - Footer at bottom
4. **Apply consistent spacing** using gap classes (gap-3 to gap-8)
5. **Use design tokens** for all colors, shadows, radius values
6. **Test responsiveness** on mobile, tablet, and desktop
7. **Check against Admin Dashboard** for visual consistency

## Common Page Sections

### Header with Actions
```javascript
<PageHeader
  title="Products"
  subtitle="Inventory"
  actions={
    <div className="flex items-center gap-3">
      <Button variant="primary">Add Product</Button>
      <Button variant="secondary">Export</Button>
    </div>
  }
/>
```

### Search and Filters
```javascript
<div className="flex flex-col md:flex-row gap-4">
  <Input 
    placeholder="Search..."
    icon={Search}
    value={searchTerm}
    onChange={(e) => setSearchTerm(e.target.value)}
  />
  <Button variant="secondary">Filters</Button>
</div>
```

### List/Grid View
```javascript
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {items.map(item => (
    <Card key={item.id} hoverable>
      {/* Item content */}
    </Card>
  ))}
</div>
```

## Next Steps

1. Update all pages using the design tokens and components
2. Remove inline styles and consolidate into design tokens
3. Test on multiple screen sizes
4. Verify visual consistency with Admin Dashboard
5. Update any custom styles to use the design system

## Files Reference

- **Design Tokens**: `lib/designTokens.js`
- **UI Components**: `components/ui/`
- **Hooks**: `hooks/useLikes.js`
- **Example**: `app/admin/dashboard/page.js`
