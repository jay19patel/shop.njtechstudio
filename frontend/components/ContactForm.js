'use client';

import React, { useState } from 'react';
import { submitContactMessage } from '../lib/api';

const ContactForm = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        subject: 'General Inquiry',
        message: ''
    });
    const [status, setStatus] = useState('idle'); // idle, loading, success, error

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.id]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setStatus('loading');
        try {
            await submitContactMessage(formData);
            setStatus('success');
            setFormData({ name: '', email: '', subject: 'General Inquiry', message: '' });
        } catch (error) {
            console.error('Failed to submit message:', error);
            setStatus('error');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex flex-col gap-5 w-full bg-white p-8 md:p-10 rounded-2xl border border-slate-100 shadow-sm relative overflow-hidden">
            
            {status === 'success' && (
                <div className="absolute inset-0 bg-white/95 backdrop-blur-sm z-10 flex flex-col items-center justify-center p-8 text-center rounded-2xl">
                    <div className="w-12 h-12 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4">
                        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" /></svg>
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">Message Sent</h3>
                    <p className="text-slate-500 text-sm max-w-xs">Thank you for reaching out. We will get back to you within 24-48 hours.</p>
                    <button type="button" onClick={() => setStatus('idle')} className="mt-6 px-4 py-2 bg-slate-100 text-slate-700 font-semibold text-sm rounded-lg hover:bg-slate-200 transition-colors">
                        Send another message
                    </button>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                <div className="flex flex-col gap-2">
                    <label htmlFor="name" className="text-xs font-semibold text-slate-600 ml-1">Your Name</label>
                    <input
                        type="text"
                        id="name"
                        value={formData.name}
                        onChange={handleChange}
                        placeholder="Jane Doe"
                        className="w-full bg-white border border-slate-200 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none"
                        required
                    />
                </div>
                <div className="flex flex-col gap-2">
                    <label htmlFor="email" className="text-xs font-semibold text-slate-600 ml-1">Email Address</label>
                    <input
                        type="email"
                        id="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="contact@njtechstudio.in"
                        className="w-full bg-white border border-slate-200 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none"
                        required
                    />
                </div>
            </div>

            <div className="flex flex-col gap-2">
                <label htmlFor="subject" className="text-xs font-semibold text-slate-600 ml-1">Subject</label>
                <select
                    id="subject"
                    value={formData.subject}
                    onChange={handleChange}
                    className="w-full bg-white border border-slate-200 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none appearance-none"
                >
                    <option>General Inquiry</option>
                    <option>Custom Order Request</option>
                    <option>Collaboration</option>
                    <option>Workshop Booking</option>
                </select>
            </div>

            <div className="flex flex-col gap-2">
                <label htmlFor="message" className="text-xs font-semibold text-slate-600 ml-1">Your Message</label>
                <textarea
                    id="message"
                    rows="4"
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Tell us about your project or inquiry..."
                    className="w-full bg-white border border-slate-200 rounded-xl py-3 px-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none resize-none"
                    required
                ></textarea>
            </div>

            {status === 'error' && (
                <p className="text-red-500 text-sm font-medium px-2">Something went wrong. Please try again.</p>
            )}

            <button
                type="submit"
                disabled={status === 'loading'}
                className="w-full bg-slate-900 text-white rounded-xl py-3 font-semibold text-sm hover:bg-slate-800 transition-all disabled:opacity-50 mt-2"
            >
                {status === 'loading' ? 'Sending...' : 'Send Message'}
            </button>
        </form>
    );
};

export default ContactForm;
