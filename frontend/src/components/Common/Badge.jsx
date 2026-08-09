import React from 'react';

export function Badge({ children, variant = "indigo" }) {
  const variants = {
    indigo: "bg-indigo-50 text-indigo-700 border-indigo-100",
    purple: "bg-purple-50 text-purple-700 border-purple-100",
    emerald: "bg-emerald-50 text-emerald-700 border-emerald-100",
    blue: "bg-blue-50 text-blue-700 border-blue-100",
  };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10.5px] font-medium border ${variants[variant] || variants.blue}`}>
      {children}
    </span>
  );
}
