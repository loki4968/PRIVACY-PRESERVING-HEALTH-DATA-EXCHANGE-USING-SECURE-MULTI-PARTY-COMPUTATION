import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './context/AuthContext';
import './globals.css';

export const metadata = {
    title: 'Health Data Exchange',
    description: 'Secure and efficient health data exchange platform',
};

export default function RootLayout({ children }) {
    return (
        <html lang="en">
            <head>
                <link
                    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
                    rel="stylesheet"
                />
            </head>
            <body className="font-inter">
                <AuthProvider>
                    {children}
                    <Toaster
                        position="top-center"
                        reverseOrder={false}
                        gutter={8}
                        toastOptions={{
                            duration: 3000,
                            style: {
                                background: '#ffffff',
                                color: '#1a1a1a',
                                padding: '16px',
                                borderRadius: '12px',
                                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                                fontSize: '14px',
                                maxWidth: '400px',
                                border: '1px solid rgba(0, 0, 0, 0.05)'
                            },
                            success: {
                                style: {
                                    background: '#f0fdf4',
                                    color: '#166534',
                                    border: '1px solid #bbf7d0'
                                },
                                iconTheme: {
                                    primary: '#22c55e',
                                    secondary: '#ffffff'
                                }
                            },
                            error: {
                                style: {
                                    background: '#fef2f2',
                                    color: '#991b1b',
                                    border: '1px solid #fecaca'
                                },
                                iconTheme: {
                                    primary: '#ef4444',
                                    secondary: '#ffffff'
                                }
                            },
                            loading: {
                                style: {
                                    background: '#f5f3ff',
                                    color: '#5b21b6',
                                    border: '1px solid #ddd6fe'
                                }
                            }
                        }}
                    />
                </AuthProvider>
            </body>
        </html>
    );
}
