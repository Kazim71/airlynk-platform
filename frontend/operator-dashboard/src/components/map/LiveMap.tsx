"use client";

import dynamic from "next/dynamic";

const MapRenderer = dynamic(() => import("./MapRenderer"), { 
  ssr: false,
  loading: () => (
    <div className="w-full h-full bg-gray-100 flex items-center justify-center text-gray-500">
      Loading map engine...
    </div>
  )
});

export function LiveMap({ drivers = [] }: { drivers?: any[] }) {
  return <MapRenderer drivers={drivers} />;
}
