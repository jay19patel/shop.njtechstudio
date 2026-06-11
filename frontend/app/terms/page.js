import React from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';

export default function TermsPage() {
    const policies = [
        {
            title: "1. No Cash on Delivery (COD)",
            desc: "All orders must be pre-paid. We currently do not offer Cash on Delivery services to ensure a streamlined and secure crafting process."
        },
        {
            title: "2. No Returns or Refunds",
            desc: "Since every item is meticulously handcrafted specifically for you, all sales are final. We do not accept returns, exchanges, or process refunds."
        },
        {
            title: "3. Order Processing & Shipping",
            desc: "Custom and standard orders typically take 10-14 days to craft and dispatch. Shipping times vary based on location. We are not responsible for delays caused by courier services."
        },
        {
            title: "4. Custom Orders",
            desc: "For bespoke items, clear communication regarding design, color, and materials is required upfront. Once crafting has begun, no modifications to the design can be made."
        },
        {
            title: "5. Privacy Policy",
            desc: "Your personal information, including contact details and shipping addresses, is strictly used for order fulfillment and communication. We do not share your data with third parties."
        }
    ];

    return (
        <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900 selection:bg-slate-900/30">
            <Navbar />

            <main className="flex-grow w-full max-w-3xl mx-auto px-4 py-12 md:py-20 flex flex-col gap-12">
                <section className="flex flex-col gap-4">
                    <h1 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
                        Store Policies
                    </h1>
                    <p className="text-slate-500 font-medium">
                        Please review our store policies, terms of service, and privacy guidelines before placing an order. By making a purchase, you agree to these terms.
                    </p>
                </section>

                <section className="flex flex-col gap-10">
                    {policies.map((policy, idx) => (
                        <div key={idx} className="flex flex-col gap-2">
                            <h3 className="text-lg font-semibold text-slate-800">
                                {policy.title}
                            </h3>
                            <p className="text-slate-600 leading-relaxed">
                                {policy.desc}
                            </p>
                        </div>
                    ))}

                    <div className="pt-8 border-t border-slate-100 flex flex-col gap-4 mt-4">
                        <p className="text-slate-500 text-sm">
                            If you have any questions or concerns, please get in touch with us via our <a href="/contact" className="text-slate-900 font-medium hover:underline transition-all">Contact Page</a>.
                        </p>
                    </div>
                </section>
            </main>

            <Footer />
        </div>
    );
}
