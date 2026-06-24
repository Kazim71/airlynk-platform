'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api } from '@/lib/api';
import { Plane, ArrowRight } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';

export default function RegisterPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const login = useAuthStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const formData = new FormData(e.currentTarget);
    const email = formData.get('email') as string;
    const password = formData.get('password') as string;
    const fullName = formData.get('full_name') as string;

    try {
      // 1. Register User
      await api.post('/auth/register', {
        email,
        password,
        full_name: fullName,
        role: 'customer' // AirLynk backend auth model
      });

      // 2. Login User automatically
      const response = await api.post('/auth/login', {
        email: email,
        password: password,
      });

      const { access_token } = response.data;

      // 3. Fetch user profile
      const userResponse = await api.get('/auth/me', {
        headers: {
          Authorization: `Bearer ${access_token}`,
        },
      });

      login(userResponse.data, access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4 py-12">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="p-8 text-center bg-blue-600 text-white">
          <div className="flex justify-center mb-4">
            <Plane className="w-12 h-12" />
          </div>
          <h1 className="text-3xl font-bold mb-2">Create Account</h1>
          <p className="text-blue-100">Join AirLynk for premium airport transfers</p>
        </div>
        
        <form onSubmit={handleSubmit} className="p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-600 rounded-xl text-sm">
              {error}
            </div>
          )}
          
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
            <input 
              name="full_name"
              type="text" 
              required
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all"
              placeholder="John Doe"
            />
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
            <input 
              name="email"
              type="email" 
              required
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all"
              placeholder="you@example.com"
            />
          </div>
          
          <div className="mb-8">
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input 
              name="password"
              type="password" 
              required
              className="w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-blue-600 focus:border-transparent outline-none transition-all"
              placeholder="••••••••"
            />
          </div>
          
          <button 
            disabled={loading}
            type="submit" 
            className="w-full bg-blue-600 hover:bg-blue-700 text-white py-4 rounded-xl font-medium transition-all flex items-center justify-center gap-2 disabled:opacity-70 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating account...' : 'Sign Up'}
            {!loading && <ArrowRight className="w-5 h-5" />}
          </button>
          
          <div className="mt-6 text-center text-gray-600">
            Already have an account?{' '}
            <Link href="/login" className="text-blue-600 font-medium hover:underline">
              Sign In
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
