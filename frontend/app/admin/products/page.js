"use client";

import React, { useState, useEffect, useCallback } from 'react';
import Navbar from '../../../components/Navbar';
import Footer from '../../../components/Footer';
import { useAuth } from '../../../context/AuthContext';
import { useRouter } from 'next/navigation';
import {
  getAdminProducts, createAdminProduct, updateAdminProduct,
  deleteAdminProduct, getCategories, getAdminCategories, createAdminCategory,
  updateAdminCategory, deleteAdminCategory,
} from '../../../lib/api';
import {
  Package, Plus, Search, Edit3, Trash2, X, ChevronLeft,
  Loader2, Tag, ImagePlus, AlertTriangle, ToggleLeft, ToggleRight,
} from 'lucide-react';
import Link from 'next/link';

const EMPTY_FORM = {
  name: '', slug: '', description: '', price: '',
  discount_percentage: '', available_quantity: '',
  category_id: '', is_active: true, image: null,
};

function slugify(str) {
  return str.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)+/g, '');
}

export default function AdminProductsPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState('');
  const [imagePreview, setImagePreview] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [toast, setToast] = useState(null);

  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState(null);
  const [categoryFormData, setCategoryFormData] = useState({ name: '', description: '', image_url: '' });
  const [savingCategory, setSavingCategory] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push('/login');
    else if (!authLoading && isAuthenticated && !user?.is_superuser) router.push('/profile');
  }, [authLoading, isAuthenticated, user, router]);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [prods, cats] = await Promise.all([getAdminProducts(), getCategories()]);
      setProducts(prods);
      setCategories(cats);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && user?.is_superuser) fetchAll();
  }, [isAuthenticated, user, fetchAll]);

  const showToast = (msg, type = 'success') => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const openModal = (product = null) => {
    setFormError('');
    if (product) {
      setEditingProduct(product);
      setFormData({
        name: product.name || '',
        slug: product.slug || '',
        description: product.description || '',
        price: product.priceValue ?? product.base_price ?? '',
        discount_percentage: product.discountPercentage ?? product.discount_percentage ?? '',
        available_quantity: product.availableQuantity ?? product.available_quantity ?? '',
        category_id: product.category_id ?? product.category?.id ?? '',
        is_active: product.is_active ?? true,
        image: null,
      });
      setImagePreview(product.image || product.primary_image || '');
    } else {
      setEditingProduct(null);
      setFormData(EMPTY_FORM);
      setImagePreview('');
    }
    setIsModalOpen(true);
  };

  const closeModal = () => { setIsModalOpen(false); setEditingProduct(null); setFormError(''); };

  const handleSave = async (e) => {
    e.preventDefault();
    setFormError('');
    if (!formData.name.trim()) return setFormError('Product name is required.');
    if (!formData.price || isNaN(Number(formData.price))) return setFormError('Valid price is required.');
    setSaving(true);
    try {
      const fd = new FormData();
      fd.append('name', formData.name.trim());
      fd.append('slug', formData.slug || slugify(formData.name));
      fd.append('description', formData.description || '');
      fd.append('price', formData.price);
      fd.append('base_price', formData.price);
      if (formData.discount_percentage !== '') fd.append('discount_percentage', formData.discount_percentage);
      if (formData.available_quantity !== '') fd.append('available_quantity', formData.available_quantity);
      if (formData.category_id) fd.append('category_id', formData.category_id);
      fd.append('is_active', formData.is_active ? 'true' : 'false');
      if (formData.image) fd.append('image', formData.image);

      if (editingProduct) {
        await updateAdminProduct(editingProduct.id, fd);
        showToast('Product updated.');
      } else {
        await createAdminProduct(fd);
        showToast('Product created.');
      }
      closeModal();
      fetchAll();
    } catch (err) {
      setFormError(err.message || 'Something went wrong.');
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteAdminProduct(deleteTarget.id);
      setDeleteTarget(null);
      showToast('Product deleted.', 'info');
      fetchAll();
    } catch {
      showToast('Failed to delete.', 'error');
    } finally {
      setDeleting(false);
    }
  };

  const filteredProducts = products.filter(p =>
    p.name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const openCategoryModal = (category = null) => {
    if (category) {
      setEditingCategory(category);
      setCategoryFormData({
        name: category.name || '',
        description: category.description || '',
        image_url: category.image_url || '',
      });
    } else {
      setEditingCategory(null);
      setCategoryFormData({ name: '', description: '', image_url: '' });
    }
    setIsCategoryModalOpen(true);
  };

  const closeCategoryModal = () => {
    setIsCategoryModalOpen(false);
    setEditingCategory(null);
    setCategoryFormData({ name: '', description: '', image_url: '' });
  };

  const handleSaveCategory = async (e) => {
    e.preventDefault();
    if (!categoryFormData.name.trim()) return;
    setSavingCategory(true);
    try {
      if (editingCategory) {
        await updateAdminCategory(editingCategory.id, categoryFormData);
        showToast('Category updated.');
      } else {
        await createAdminCategory(categoryFormData);
        showToast('Category created.');
      }
      closeCategoryModal();
      fetchAll();
    } catch (err) {
      showToast(err.message || 'Failed to save category.', 'error');
    } finally {
      setSavingCategory(false);
    }
  };

  const handleDeleteCategory = async (categoryId) => {
    if (!confirm('Delete this category? Products will keep their category assignment.')) return;
    try {
      await deleteAdminCategory(categoryId);
      showToast('Category deleted.', 'info');
      fetchAll();
    } catch {
      showToast('Failed to delete category.', 'error');
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
        </main>
      </div>
    );
  }

  if (!user?.is_superuser) return null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Navbar />

      {/* Toast */}
      {toast && (
        <div className={`fixed top-5 right-5 z-[100] px-4 py-3 rounded-lg shadow-lg text-sm font-semibold ${
          toast.type === 'error' ? 'bg-red-600 text-white' :
          toast.type === 'info' ? 'bg-slate-800 text-white' : 'bg-emerald-600 text-white'
        }`}>
          {toast.msg}
        </div>
      )}

      <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col gap-8">

          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <Link href="/admin/dashboard" className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-700 uppercase tracking-wider font-bold mb-1 w-fit transition-colors">
                <ChevronLeft className="w-3.5 h-3.5" /> Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-slate-900">Products</h1>
              <p className="text-xs text-slate-400 mt-0.5">{products.length} total products</p>
            </div>
            <button
              onClick={() => openModal()}
              className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors"
            >
              <Plus className="w-4 h-4" /> Add Product
            </button>
          </div>

          {/* Table */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-bold text-slate-900">All Products</h2>
                <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">{filteredProducts.length}</span>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[700px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <th className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider w-16">Image</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Product</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Category</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Price</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Stock</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProducts.length === 0 ? (
                    <tr>
                      <td colSpan="7" className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center gap-2 text-slate-400">
                          <Package className="w-8 h-8" />
                          <span className="text-sm">No products found</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredProducts.map((product) => (
                    <tr key={product.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors group">
                      <td className="px-6 py-3 align-middle">
                        <div className="w-10 h-10 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center">
                          {product.image || product.primary_image ? (
                            <img src={product.image || product.primary_image} alt={product.name} className="w-full h-full object-cover" />
                          ) : (
                            <Package className="w-4 h-4 text-slate-300" />
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <div className="flex flex-col gap-0.5">
                          <span className="font-semibold text-sm text-slate-900">{product.name}</span>
                          <span className="text-[10px] text-slate-400 font-mono">{product.slug}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <span className="text-xs text-slate-600 bg-slate-100 px-2 py-0.5 rounded-md font-medium">
                          {typeof product.category === 'object' ? product.category?.name : product.category || '—'}
                        </span>
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <div className="flex flex-col gap-0.5">
                          <span className="font-bold text-sm text-slate-900">₹{Number(product.priceValue ?? product.base_price ?? 0).toLocaleString('en-IN')}</span>
                          {Number(product.discountPercentage || product.discount_percentage || 0) > 0 && (
                            <span className="text-[10px] text-orange-500 font-medium">{product.discountPercentage || product.discount_percentage}% off</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <span className={`text-xs font-semibold px-2 py-0.5 rounded-md ${
                          Number(product.availableQuantity ?? product.available_quantity ?? 0) > 5
                            ? 'bg-emerald-50 text-emerald-700'
                            : Number(product.availableQuantity ?? product.available_quantity ?? 0) > 0
                            ? 'bg-orange-50 text-orange-600'
                            : 'bg-red-50 text-red-600'
                        }`}>
                          {product.availableQuantity ?? product.available_quantity ?? 0} left
                        </span>
                      </td>
                      <td className="px-4 py-3 align-middle">
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-md ${
                          product.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'
                        }`}>
                          {product.is_active ? 'Active' : 'Hidden'}
                        </span>
                      </td>
                      <td className="px-4 py-3 align-middle text-right">
                        <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => openModal(product)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => setDeleteTarget(product)} className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          {/* Categories Section */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden mt-8">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-bold text-slate-900">Categories</h2>
                <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">{categories.length}</span>
              </div>
              <button
                onClick={() => openCategoryModal()}
                className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors"
              >
                <Plus className="w-4 h-4" /> Add Category
              </button>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[500px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <th className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Category</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Description</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {categories.length === 0 ? (
                    <tr>
                      <td colSpan="3" className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center gap-2 text-slate-400">
                          <Tag className="w-8 h-8" />
                          <span className="text-sm">No categories found</span>
                        </div>
                      </td>
                    </tr>
                  ) : categories.map((cat) => (
                    <tr key={cat.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors group">
                      <td className="px-6 py-4 align-middle">
                        <span className="font-semibold text-sm text-slate-900">{cat.name}</span>
                      </td>
                      <td className="px-4 py-4 align-middle">
                        <span className="text-xs text-slate-600 line-clamp-2">{cat.description || '—'}</span>
                      </td>
                      <td className="px-4 py-4 align-middle text-right">
                        <div className="flex items-center justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => openCategoryModal(cat)} className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                            <Edit3 className="w-3.5 h-3.5" />
                          </button>
                          <button onClick={() => handleDeleteCategory(cat.id)} className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      {/* ── Add/Edit Modal ── */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={(e) => e.target === e.currentTarget && closeModal()}>
          <div className="bg-white rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <div>
                <h3 className="text-base font-bold text-slate-900">{editingProduct ? 'Edit Product' : 'Add New Product'}</h3>
                {editingProduct && <p className="text-xs text-slate-400 mt-0.5">ID #{editingProduct.id}</p>}
              </div>
              <button onClick={closeModal} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSave} className="flex flex-col overflow-y-auto flex-grow">
              <div className="p-6 flex flex-col gap-5">
                {formError && (
                  <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-xs font-semibold px-3 py-2.5 rounded-lg">
                    <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" /> {formError}
                  </div>
                )}

                {/* Image */}
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Product Image</label>
                  <div className="flex items-start gap-3">
                    <div className="w-20 h-20 rounded-lg bg-slate-100 border border-slate-200 overflow-hidden flex items-center justify-center flex-shrink-0">
                      {imagePreview ? <img src={imagePreview} alt="Preview" className="w-full h-full object-cover" /> : <Package className="w-6 h-6 text-slate-300" />}
                    </div>
                    <label className="flex-1 flex flex-col items-center justify-center h-20 border border-dashed border-slate-300 rounded-lg cursor-pointer hover:border-slate-400 hover:bg-slate-50 transition-all">
                      <ImagePlus className="w-4 h-4 text-slate-400 mb-1" />
                      <span className="text-xs text-slate-400">Click to upload</span>
                      <input type="file" accept="image/*" onChange={(e) => {
                        const file = e.target.files[0];
                        if (file) { setFormData(p => ({ ...p, image: file })); setImagePreview(URL.createObjectURL(file)); }
                      }} className="hidden" />
                    </label>
                  </div>
                </div>

                {/* Name + Slug */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Name <span className="text-red-400">*</span></label>
                    <input type="text" required placeholder="Product name" value={formData.name}
                      onChange={(e) => setFormData(p => ({ ...p, name: e.target.value, slug: editingProduct ? p.slug : slugify(e.target.value) }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Slug</label>
                    <input type="text" placeholder="auto-generated" value={formData.slug}
                      onChange={(e) => setFormData(p => ({ ...p, slug: e.target.value }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm font-mono outline-none focus:border-slate-400 focus:bg-white transition-all" />
                  </div>
                </div>

                {/* Price + Discount + Qty */}
                <div className="grid grid-cols-3 gap-3">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Price (₹) <span className="text-red-400">*</span></label>
                    <input type="number" required min="0" step="0.01" placeholder="0.00" value={formData.price}
                      onChange={(e) => setFormData(p => ({ ...p, price: e.target.value }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Discount %</label>
                    <input type="number" min="0" max="100" step="0.01" placeholder="0" value={formData.discount_percentage}
                      onChange={(e) => setFormData(p => ({ ...p, discount_percentage: e.target.value }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Quantity</label>
                    <input type="number" min="0" placeholder="0" value={formData.available_quantity}
                      onChange={(e) => setFormData(p => ({ ...p, available_quantity: e.target.value }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                  </div>
                </div>

                {/* Category + Active */}
                <div className="grid grid-cols-2 gap-3">
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1"><Tag className="w-3 h-3" /> Category</label>
                    <select value={formData.category_id} onChange={(e) => setFormData(p => ({ ...p, category_id: e.target.value }))}
                      className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all appearance-none cursor-pointer">
                      <option value="">— Select —</option>
                      {categories.map(cat => <option key={cat.id} value={cat.id}>{cat.name}</option>)}
                    </select>
                  </div>
                  <div className="flex flex-col gap-1.5">
                    <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Visibility</label>
                    <button type="button" onClick={() => setFormData(p => ({ ...p, is_active: !p.is_active }))}
                      className={`flex items-center gap-2 py-2 px-3 rounded-lg border text-sm font-semibold transition-all ${
                        formData.is_active ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-slate-50 border-slate-200 text-slate-500'
                      }`}>
                      {formData.is_active ? <ToggleRight className="w-4 h-4" /> : <ToggleLeft className="w-4 h-4" />}
                      {formData.is_active ? 'Active' : 'Hidden'}
                    </button>
                  </div>
                </div>

                {/* Description */}
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Description</label>
                  <textarea rows={3} placeholder="Product description..." value={formData.description}
                    onChange={(e) => setFormData(p => ({ ...p, description: e.target.value }))}
                    className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all resize-none" />
                </div>
              </div>

              <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2 bg-slate-50/50">
                <button type="button" onClick={closeModal} className="px-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">Cancel</button>
                <button type="submit" disabled={saving} className="flex items-center gap-2 px-5 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50">
                  {saving && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {editingProduct ? 'Save Changes' : 'Create Product'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirm */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-sm shadow-2xl p-6 flex flex-col gap-5">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 bg-red-50 rounded-lg flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Delete Product?</h3>
                <p className="text-xs text-slate-500 mt-1"><span className="font-semibold text-slate-700">{deleteTarget.name}</span> will be permanently removed.</p>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteTarget(null)} disabled={deleting} className="px-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-500 hover:bg-slate-50 rounded-lg transition-colors">Cancel</button>
              <button onClick={confirmDelete} disabled={deleting} className="flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-red-700 transition-colors disabled:opacity-60">
                {deleting && <Loader2 className="w-3 h-3 animate-spin" />} Delete
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Category Modal ── */}
      {isCategoryModalOpen && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={(e) => e.target === e.currentTarget && closeCategoryModal()}>
          <div className="bg-white rounded-xl w-full max-w-lg shadow-2xl overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <h3 className="text-base font-bold text-slate-900">{editingCategory ? 'Edit Category' : 'Add New Category'}</h3>
              <button onClick={closeCategoryModal} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
                <X className="w-4 h-4" />
              </button>
            </div>

            <form onSubmit={handleSaveCategory} className="flex flex-col">
              <div className="p-6 flex flex-col gap-4">
                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Name <span className="text-red-400">*</span></label>
                  <input type="text" required placeholder="Category name" value={categoryFormData.name}
                    onChange={(e) => setCategoryFormData(p => ({ ...p, name: e.target.value }))}
                    className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Description</label>
                  <textarea rows={3} placeholder="Category description..." value={categoryFormData.description}
                    onChange={(e) => setCategoryFormData(p => ({ ...p, description: e.target.value }))}
                    className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all resize-none" />
                </div>

                <div className="flex flex-col gap-1.5">
                  <label className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Image URL</label>
                  <input type="url" placeholder="https://..." value={categoryFormData.image_url}
                    onChange={(e) => setCategoryFormData(p => ({ ...p, image_url: e.target.value }))}
                    className="bg-slate-50 border border-slate-200 rounded-lg py-2 px-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all" />
                </div>
              </div>

              <div className="px-6 py-4 border-t border-slate-100 flex justify-end gap-2 bg-slate-50/50">
                <button type="button" onClick={closeCategoryModal} className="px-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-500 hover:bg-slate-100 rounded-lg transition-colors">Cancel</button>
                <button type="submit" disabled={savingCategory} className="flex items-center gap-2 px-5 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50">
                  {savingCategory && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
                  {editingCategory ? 'Save Changes' : 'Create Category'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
