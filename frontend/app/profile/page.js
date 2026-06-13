"use client";

import React, { useState, useEffect } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import { useAuth } from '../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { User, Lock, Save, AlertCircle, CheckCircle2, MapPin, Phone, Plus, Star } from 'lucide-react';
import { getAddresses, addAddress, setDefaultAddress, getContacts, addContact, setDefaultContact, getUserLikes } from '../../lib/api';

export default function ProfilePage() {
  const { user, isAuthenticated, loading: authLoading, updateUserProfile } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState('profile'); // profile, addresses, contacts, likes

  const [formData, setFormData] = useState({
    full_name: '',
    password: '',
    confirm_password: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Address State
  const [addresses, setAddresses] = useState([]);
  const [showAddAddress, setShowAddAddress] = useState(false);
  const [addressForm, setAddressForm] = useState({ full_name: '', address_line: '', city: '', state: '', pincode: '', is_default: false });

  // Contact State
  const [contacts, setContacts] = useState([]);
  const [showAddContact, setShowAddContact] = useState(false);
  const [contactForm, setContactForm] = useState({ phone_number: '', is_default: false });

  // Likes State
  const [likedProducts, setLikedProducts] = useState([]);
  const [likesLoading, setLikesLoading] = useState(false);

  useEffect(() => {
    if (user) {
      setFormData((prev) => ({
        ...prev,
        full_name: user.full_name || user.name || '',
      }));
    }
  }, [user]);

  useEffect(() => {
    // Only redirect when auth check is fully complete (not still loading)
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [authLoading, isAuthenticated, router]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchAddresses();
      fetchContacts();
      fetchLikes();
    }
  }, [isAuthenticated]);

  // Show nothing while auth is still being determined
  if (authLoading || !isAuthenticated) return null;

  // --- Profile Logic ---
  const handleProfileChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleProfileSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (formData.password && formData.password !== formData.confirm_password) {
      setError('Passwords do not match');
      return;
    }

    setLoading(true);
    const payload = { full_name: formData.full_name };
    if (formData.password) {
      payload.password = formData.password;
    }

    const result = await updateUserProfile(payload);
    setLoading(false);

    if (result.success) {
      setSuccess('Profile updated successfully!');
      setFormData((prev) => ({ ...prev, password: '', confirm_password: '' }));
    } else {
      setError(result.error || 'Failed to update profile');
    }
  };

  // --- Address Logic ---
  const fetchAddresses = async () => {
    try {
      const data = await getAddresses();
      setAddresses(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAddressSubmit = async (e) => {
    e.preventDefault();
    try {
      await addAddress(addressForm);
      setAddressForm({ full_name: '', address_line: '', city: '', state: '', pincode: '', is_default: false });
      setShowAddAddress(false);
      fetchAddresses();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSetDefaultAddress = async (id) => {
    try {
      await setDefaultAddress(id);
      fetchAddresses();
    } catch (err) {
      console.error(err);
    }
  };

  // --- Contact Logic ---
  const fetchContacts = async () => {
    try {
      const data = await getContacts();
      setContacts(data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleContactSubmit = async (e) => {
    e.preventDefault();
    try {
      await addContact(contactForm);
      setContactForm({ phone_number: '', is_default: false });
      setShowAddContact(false);
      fetchContacts();
    } catch (err) {
      console.error(err);
    }
  };

  const handleSetDefaultContact = async (id) => {
    try {
      await setDefaultContact(id);
      fetchContacts();
    } catch (err) {
      console.error(err);
    }
  };

  // --- Likes Logic ---
  const fetchLikes = async () => {
    setLikesLoading(true);
    try {
      const data = await getUserLikes();
      setLikedProducts(data || []);
    } catch (err) {
      console.error('Failed to fetch likes:', err);
      setLikedProducts([]);
    } finally {
      setLikesLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900">
      <Navbar />

      <main className="flex-grow w-full max-w-5xl mx-auto px-4 py-12 md:py-20 flex flex-col md:flex-row gap-8">
        
        {/* Sidebar */}
        <div className="w-full md:w-64 flex flex-col gap-2">
          <button onClick={() => setActiveTab('profile')} className={`p-4 rounded-2xl flex items-center gap-3 transition-all ${activeTab === 'profile' ? 'bg-slate-900 text-white shadow-lg' : 'bg-white hover:bg-slate-50 text-slate-600'}`}>
            <User className="w-5 h-5" />
            <span className="font-bold text-sm uppercase tracking-wider">Profile</span>
          </button>
          <button onClick={() => setActiveTab('addresses')} className={`p-4 rounded-2xl flex items-center gap-3 transition-all ${activeTab === 'addresses' ? 'bg-slate-900 text-white shadow-lg' : 'bg-white hover:bg-slate-50 text-slate-600'}`}>
            <MapPin className="w-5 h-5" />
            <span className="font-bold text-sm uppercase tracking-wider">Addresses</span>
          </button>
          <button onClick={() => setActiveTab('contacts')} className={`p-4 rounded-2xl flex items-center gap-3 transition-all ${activeTab === 'contacts' ? 'bg-slate-900 text-white shadow-lg' : 'bg-white hover:bg-slate-50 text-slate-600'}`}>
            <Phone className="w-5 h-5" />
            <span className="font-bold text-sm uppercase tracking-wider">Contacts</span>
          </button>
          <button onClick={() => { setActiveTab('likes'); fetchLikes(); }} className={`p-4 rounded-2xl flex items-center gap-3 transition-all ${activeTab === 'likes' ? 'bg-slate-900 text-white shadow-lg' : 'bg-white hover:bg-slate-50 text-slate-600'}`}>
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
              <path d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
            </svg>
            <span className="font-bold text-sm uppercase tracking-wider">Liked Products</span>
          </button>

        </div>

        {/* Content Area */}
        <div className="flex-grow bg-white rounded-[40px] shadow-xl shadow-slate-200/50 border border-slate-100 p-8 relative overflow-hidden">
          
          {/* PROFILE TAB */}
          {activeTab === 'profile' && (
            <div className="flex flex-col gap-6">
              <h2 className="text-2xl font-extrabold tracking-tight uppercase text-blue-950">
                Profile Settings
              </h2>
              {error && <div className="text-red-500">{error}</div>}
              {success && <div className="text-green-500">{success}</div>}

              <form onSubmit={handleProfileSubmit} className="flex flex-col gap-5 max-w-md">
                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Email Address</label>
                  <input disabled value={user?.email || ''} className="w-full bg-slate-50 text-slate-500 border-none rounded-2xl py-4 px-4 text-sm cursor-not-allowed" />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Full Name</label>
                  <input name="full_name" required value={formData.full_name} onChange={handleProfileChange} className="w-full bg-white rounded-2xl py-4 px-4 text-sm focus:ring-2 focus:ring-slate-900 outline-none" />
                </div>

                <div className="flex flex-col gap-2">
                  <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">New Password</label>
                  <input name="password" type="password" value={formData.password} onChange={handleProfileChange} placeholder="Leave blank to keep current" className="w-full bg-white rounded-2xl py-4 px-4 text-sm focus:ring-2 focus:ring-slate-900 outline-none" />
                </div>

                {formData.password && (
                  <div className="flex flex-col gap-2">
                    <label className="text-[10px] font-black uppercase tracking-widest text-slate-400 ml-4">Confirm New Password</label>
                    <input name="confirm_password" type="password" value={formData.confirm_password} onChange={handleProfileChange} className="w-full bg-white rounded-2xl py-4 px-4 text-sm focus:ring-2 focus:ring-slate-900 outline-none" />
                  </div>
                )}

                <button type="submit" disabled={loading} className="w-full bg-slate-900 text-white rounded-2xl py-4 font-black uppercase tracking-widest text-sm shadow-xl hover:bg-slate-900/90 transition-all flex items-center justify-center gap-3">
                  {loading ? 'Saving...' : 'Save Changes'}
                </button>
              </form>
            </div>
          )}

          {/* ADDRESSES TAB */}
          {activeTab === 'addresses' && (
            <div className="flex flex-col gap-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-extrabold tracking-tight uppercase text-blue-950">Saved Addresses</h2>
                <button onClick={() => setShowAddAddress(!showAddAddress)} className="bg-slate-900 text-white p-2 rounded-full hover:bg-orange-600 transition-all">
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              {showAddAddress && (
                <form onSubmit={handleAddressSubmit} className="bg-white border border-slate-100 shadow-sm p-6 rounded-3xl flex flex-col gap-4">
                  <input placeholder="Full Name" required value={addressForm.full_name} onChange={(e) => setAddressForm({...addressForm, full_name: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" />
                  <textarea placeholder="Address Line" required value={addressForm.address_line} onChange={(e) => setAddressForm({...addressForm, address_line: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" rows={2} />
                  <div className="grid grid-cols-2 gap-4">
                    <input placeholder="City" required value={addressForm.city} onChange={(e) => setAddressForm({...addressForm, city: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" />
                    <input placeholder="State" required value={addressForm.state} onChange={(e) => setAddressForm({...addressForm, state: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" />
                  </div>
                  <input placeholder="Pincode" required value={addressForm.pincode} onChange={(e) => setAddressForm({...addressForm, pincode: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" />
                  <label className="flex items-center gap-2 text-sm text-slate-600 font-bold uppercase tracking-widest mt-2 cursor-pointer">
                    <input type="checkbox" checked={addressForm.is_default} onChange={(e) => setAddressForm({...addressForm, is_default: e.target.checked})} className="w-4 h-4 rounded text-slate-900" />
                    Set as default address
                  </label>
                  <button type="submit" className="bg-slate-900 text-white rounded-xl py-3 font-bold text-sm hover:bg-slate-900/90">Save Address</button>
                </form>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {addresses.length === 0 && !showAddAddress && <p className="text-slate-500 text-sm">No saved addresses.</p>}
                {addresses.map(addr => (
                  <div key={addr.id} className={`p-5 rounded-2xl border-2 ${addr.is_default ? 'border-slate-200 bg-slate-100' : 'border-slate-100 bg-white'}`}>
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-bold text-blue-950">{addr.full_name}</span>
                      {addr.is_default ? (
                        <span className="bg-slate-900 text-white text-[9px] font-bold px-2 py-1 rounded-full uppercase">Default</span>
                      ) : (
                        <button onClick={() => handleSetDefaultAddress(addr.id)} className="text-[10px] font-bold text-slate-400 hover:text-slate-900 uppercase">Set Default</button>
                      )}
                    </div>
                    <p className="text-sm text-slate-600">{addr.address_line}</p>
                    <p className="text-sm text-slate-600">{addr.city}, {addr.state} - {addr.pincode}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* CONTACTS TAB */}
          {activeTab === 'contacts' && (
            <div className="flex flex-col gap-6">
              <div className="flex justify-between items-center">
                <h2 className="text-2xl font-extrabold tracking-tight uppercase text-blue-950">Saved Contacts</h2>
                <button onClick={() => setShowAddContact(!showAddContact)} className="bg-slate-900 text-white p-2 rounded-full hover:bg-orange-600 transition-all">
                  <Plus className="w-5 h-5" />
                </button>
              </div>

              {showAddContact && (
                <form onSubmit={handleContactSubmit} className="bg-white border border-slate-100 shadow-sm p-6 rounded-3xl flex flex-col gap-4">
                  <input placeholder="Phone Number" required value={contactForm.phone_number} onChange={(e) => setContactForm({...contactForm, phone_number: e.target.value})} className="w-full bg-slate-50 border border-slate-100 rounded-xl py-3 px-4 text-sm focus:outline-none focus:ring-2 focus:ring-slate-900/20" />
                  <label className="flex items-center gap-2 text-sm text-slate-600 font-bold uppercase tracking-widest mt-2 cursor-pointer">
                    <input type="checkbox" checked={contactForm.is_default} onChange={(e) => setContactForm({...contactForm, is_default: e.target.checked})} className="w-4 h-4 rounded text-slate-900" />
                    Set as default contact
                  </label>
                  <button type="submit" className="bg-slate-900 text-white rounded-xl py-3 font-bold text-sm hover:bg-slate-900/90">Save Contact</button>
                </form>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {contacts.length === 0 && !showAddContact && <p className="text-slate-500 text-sm">No saved contacts.</p>}
                {contacts.map(contact => (
                  <div key={contact.id} className={`p-5 rounded-2xl border-2 flex justify-between items-center ${contact.is_default ? 'border-slate-200 bg-slate-100' : 'border-slate-100 bg-white'}`}>
                    <span className="font-bold text-blue-950">{contact.phone_number}</span>
                    {contact.is_default ? (
                      <span className="bg-slate-900 text-white text-[9px] font-bold px-2 py-1 rounded-full uppercase">Default</span>
                    ) : (
                      <button onClick={() => handleSetDefaultContact(contact.id)} className="text-[10px] font-bold text-slate-400 hover:text-slate-900 uppercase">Set Default</button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* LIKES TAB */}
          {activeTab === 'likes' && (
            <div className="flex flex-col gap-6">
              <h2 className="text-2xl font-extrabold tracking-tight uppercase text-blue-950">
                Your Liked Products
              </h2>

              {likesLoading ? (
                <div className="text-slate-500 text-sm">Loading...</div>
              ) : likedProducts.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-100 flex items-center justify-center">
                    <svg className="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                    </svg>
                  </div>
                  <p className="text-slate-500 text-sm">You haven't liked any products yet.</p>
                  <a href="/shop" className="text-blue-950 font-bold text-sm mt-4 inline-block hover:underline">
                    Browse Products →
                  </a>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {likedProducts.map((like) => (
                    <div key={like.id} className="p-4 rounded-2xl border border-slate-100 bg-white hover:shadow-lg transition-all">
                      {like.product_image && (
                        <img
                          src={like.product_image}
                          alt={like.product_name}
                          className="w-full h-40 object-cover rounded-xl mb-4"
                        />
                      )}
                      <h3 className="font-bold text-slate-900 text-sm mb-2 line-clamp-2">
                        {like.product_name}
                      </h3>
                      <div className="flex items-baseline gap-2 mb-3">
                        <span className="text-lg font-black text-slate-900">
                          ₹{like.current_price?.toFixed(2) || 0}
                        </span>
                        {like.price_when_liked && like.price_when_liked !== like.current_price && (
                          <span className="text-xs text-slate-400 line-through">
                            ₹{like.price_when_liked?.toFixed(2) || 0}
                          </span>
                        )}
                      </div>
                      <p className="text-[10px] text-slate-400 uppercase tracking-widest font-bold mb-4">
                        Liked {new Date(like.liked_date).toLocaleDateString()}
                      </p>
                      <a
                        href={`/shop/${like.product_id}`}
                        className="w-full block bg-slate-900 text-white text-center py-2 rounded-lg text-sm font-bold hover:bg-slate-800 transition-all"
                      >
                        View Product
                      </a>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </div>
      </main>

      <Footer />
    </div>
  );
}
