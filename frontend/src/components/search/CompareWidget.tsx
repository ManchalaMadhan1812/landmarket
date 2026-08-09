import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useCompareStore, MAX_COMPARE } from '../../stores/compareStore';
import { searchProperties } from '../../services/searchService';
import { XMarkIcon, ScaleIcon, TrashIcon, ArrowRightIcon } from '@heroicons/react/24/outline';

const CompareWidget: React.FC = () => {
  const { propertyIds, removeProperty, clearComparison } = useCompareStore();

  const { data } = useQuery({
    queryKey: ['compareWidgetData', propertyIds],
    queryFn: () => searchProperties({ ids: propertyIds }),
    enabled: propertyIds.length > 0,
  });

  if (propertyIds.length === 0) {
    return null;
  }

  const properties = data?.results || [];

  return (
    <div className="fixed bottom-5 right-5 left-5 md:left-auto z-50 max-w-xl w-full bg-white/95 backdrop-blur-md rounded-2xl shadow-2xl border border-gray-200 p-4 animate-fade-in-up transition-all">
      {/* Widget Header */}
      <div className="flex items-center justify-between mb-3 border-b border-gray-100 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-primary-100 text-primary-700 rounded-lg">
            <ScaleIcon className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-gray-900 text-sm">Property Comparison Bar</h4>
            <p className="text-[11px] text-gray-500">
              {propertyIds.length} of {MAX_COMPARE} properties selected
            </p>
          </div>
        </div>

        <button
          onClick={clearComparison}
          className="text-xs text-gray-400 hover:text-red-600 flex items-center gap-1 transition-colors"
          title="Clear comparison list"
        >
          <TrashIcon className="w-3.5 h-3.5" />
          <span>Clear</span>
        </button>
      </div>

      {/* Property Thumbnails Preview Strip */}
      <div className="grid grid-cols-4 gap-2 mb-3">
        {Array.from({ length: MAX_COMPARE }).map((_, index) => {
          const property = properties[index];
          const propertyId = propertyIds[index];

          if (propertyId && property) {
            return (
              <div
                key={propertyId}
                className="relative bg-gray-50 rounded-xl border border-gray-200 p-1.5 flex flex-col items-center group"
              >
                <button
                  onClick={() => removeProperty(propertyId)}
                  className="absolute -top-1.5 -right-1.5 bg-white text-gray-400 hover:text-red-500 hover:bg-red-50 p-0.5 rounded-full shadow border border-gray-200 transition-colors z-10"
                  title="Remove from comparison"
                >
                  <XMarkIcon className="w-3.5 h-3.5" />
                </button>
                <div className="w-full h-12 rounded-lg overflow-hidden bg-gray-200 mb-1">
                  {property.primary_image ? (
                    <img
                      src={property.primary_image}
                      alt={property.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center text-xs">🏠</div>
                  )}
                </div>
                <span className="text-[10px] font-semibold text-gray-800 truncate w-full text-center">
                  {property.title}
                </span>
              </div>
            );
          }

          if (propertyId && !property) {
            return (
              <div
                key={propertyId}
                className="relative bg-gray-50 rounded-xl border border-gray-200 p-1.5 flex items-center justify-center h-20 animate-pulse"
              >
                <span className="text-[10px] text-gray-400">Loading...</span>
              </div>
            );
          }

          return (
            <div
              key={`empty-${index}`}
              className="bg-gray-50/50 rounded-xl border border-dashed border-gray-300 p-1.5 flex items-center justify-center h-20 text-center"
            >
              <span className="text-[10px] text-gray-400">Empty Slot</span>
            </div>
          );
        })}
      </div>

      {/* Action Footer */}
      <div className="flex items-center gap-2">
        {propertyIds.length < 2 && (
          <p className="text-[11px] text-amber-700 bg-amber-50 px-3 py-1.5 rounded-lg flex-1 font-medium">
            ⚠️ Select at least 2 properties to launch compare
          </p>
        )}
        <Link
          to="/compare"
          className={`py-2.5 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-bold text-center flex items-center justify-center gap-1.5 transition-all shadow-md ${
            propertyIds.length < 2 ? 'opacity-50 pointer-events-none' : 'flex-1'
          }`}
        >
          <span>Compare Side-by-Side</span>
          <ArrowRightIcon className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
};

export default CompareWidget;
