import { Geist } from "next/font/google";
import "./globals.css";
import { CartProvider } from "../context/CartContext";
import { GoogleOAuthProvider } from "@react-oauth/google";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});



export const metadata = {
  title: "NJShop | Premium E-commerce Store",
  description: "Discover our premium collection of accessories, home decor, and curated designs at NJShop.",
  icons: {
    icon: '/favicon.ico',
  },
};

import { AuthProvider } from "../context/AuthContext";
import MarqueeBanner from "../components/MarqueeBanner";
import ChatBot from "../components/ChatBot";

export default function RootLayout({ children }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <GoogleOAuthProvider clientId={process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID || "your_google_client_id_here.apps.googleusercontent.com"}>
          <AuthProvider>
            <CartProvider>
              <MarqueeBanner />
              {children}
              <ChatBot />
            </CartProvider>
          </AuthProvider>
        </GoogleOAuthProvider>
      </body>

    </html>
  );
}
