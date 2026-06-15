"use client";

import React, { createContext, useContext, useState } from "react";

const TabsContext = createContext<{
  activeTab: string;
  setActiveTab: (value: string) => void;
}>({
  activeTab: "",
  setActiveTab: () => {},
});

export function Tabs({ defaultValue, children, className = "" }: { defaultValue: string; children: React.ReactNode; className?: string }) {
  const [activeTab, setActiveTab] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ activeTab, setActiveTab }}>
      <div className={className}>{children}</div>
    </TabsContext.Provider>
  );
}

export function TabsList({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`flex space-x-2 border-b ${className}`}>{children}</div>;
}

export function TabsTrigger({ value, children }: { value: string; children: React.ReactNode }) {
  const { activeTab, setActiveTab } = useContext(TabsContext);
  const isActive = activeTab === value;
  
  return (
    <button
      onClick={() => setActiveTab(value)}
      className={`px-4 py-2 font-medium text-sm transition-colors border-b-2 ${
        isActive 
          ? "border-blue-600 text-blue-600" 
          : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
      }`}
    >
      {children}
    </button>
  );
}

export function TabsContent({ value, children, className = "" }: { value: string; children: React.ReactNode; className?: string }) {
  const { activeTab } = useContext(TabsContext);
  
  if (activeTab !== value) return null;
  return <div className={`pt-4 ${className}`}>{children}</div>;
}
