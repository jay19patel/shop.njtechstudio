import React from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import ContactForm from '../../components/ContactForm';
import siteData from '../../data/siteData.json';

export default function ContactPage() {
    const { brand } = siteData;

    const requirements = [
        { title: "Project Inspiration", desc: "Attach images or links to designs you love so we can understand your style." },
        { title: "Dimensions", desc: "Specify the approximate width, height, or diameter you'd like for your custom piece." },
        { title: "Timeline", desc: "When do you need it? Most custom orders take 10-14 days to craft and deliver." }
    ];

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900 selection:bg-slate-900/30">
            <Navbar />

            <main className="flex-grow w-full max-w-6xl mx-auto px-4 py-16 md:py-24 flex flex-col items-center gap-24">


                {/* Form and Requirements Grid */}
                <section className="w-full grid grid-cols-1 lg:grid-cols-2 gap-16 items-start">

                    {/* Left: Contact Form */}
                    <div className="flex flex-col gap-6 order-2 lg:order-1">
                        <h3 className="text-2xl font-bold tracking-tight text-slate-900">
                            Send a Message
                        </h3>
                        <ContactForm />
                    </div>

                    {/* Right: Requirements */}
                    <div className="flex flex-col gap-10 order-1 lg:order-2 bg-white p-8 md:p-10 rounded-2xl border border-slate-100 shadow-sm">
                        <div className="flex flex-col gap-3">
                            <h3 className="text-xl font-semibold tracking-tight text-slate-900">
                                Custom Order Requirements
                            </h3>
                            <p className="text-slate-500 text-sm">
                                For custom handcrafted requests, please include the following details in your message to help us provide an accurate quote:
                            </p>
                        </div>

                        <div className="flex flex-col gap-6">
                            {requirements.map((req, idx) => (
                                <div key={idx} className="flex gap-4">
                                    <div className="w-6 h-6 rounded-full bg-slate-900 text-white flex-shrink-0 flex items-center justify-center font-bold text-xs mt-0.5">
                                        {idx + 1}
                                    </div>
                                    <div className="flex flex-col gap-1">
                                        <h5 className="font-semibold text-slate-900 text-sm">{req.title}</h5>
                                        <p className="text-slate-500 text-sm">{req.desc}</p>
                                    </div>
                                </div>
                            ))}
                        </div>

                        <div className="pt-8 border-t border-slate-200 flex flex-col gap-3">
                            <h4 className="text-slate-900 font-semibold text-sm">Direct Contact</h4>
                            <div className="flex flex-col gap-1">
                                <a href={`mailto:${brand.email}`} className="text-slate-600 hover:text-slate-900 transition-colors text-sm">{brand.email}</a>
                                {brand.phone && (
                                    <a href={`tel:${brand.phone.replace(/\s+/g, '')}`} className="text-slate-600 hover:text-slate-900 transition-colors text-sm">{brand.phone}</a>
                                )}
                            </div>
                            <p className="text-slate-400 text-sm mt-1">Based in {brand.location}</p>
                        </div>
                    </div>
                </section>

            </main>

            <Footer />
        </div >
    );
}
