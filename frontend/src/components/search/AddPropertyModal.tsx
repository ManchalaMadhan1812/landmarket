import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { searchProperties } from '../../services/searchService';
import { MagnifyingGlassIcon, XMarkIcon, PlusIcon, CheckIcon } from '@heroicons/react/24/outline';
import LoadingSpinner from '../ui/LoadingSpinner';

interface AddPropertyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectProperty: (id: string) => void;
  currentPropertyIds: string[];
}

const AddPropertyModal: React.FC<AddPropertyModalProps> = ({
  isOpen,
  onClose,
  onSelectProperty,
  currentPropertyIds,
}) => {
  const [searchQuery, setSearchQuery] = useState('');

  const { data, isLoading } = useQuery({
    queryKey: ['addPropertyModalSearch', searchQuery],
    queryFn: () => searchProperties({ q: searchQuery, page_size: 10 }),
    enabled: isOpen,
  });

  if (!isOpen) return null;

  const results = data?.results || [];

  const formatPrice = (price: number) => {
    if (price >= 10000000) {
      return `₹${(price / 10000000).toFixed(2)} Cr`;
    } else if (price >= 100000) {
      return `₹${(price / 100000).toFixed(2)} L`;
    }
    return `₹${price.toLocaleString()}`;
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] flex flex-col shadow-2xl overflow-hidden animate-fade-in">
        {/* Modal Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
          <div>
            <h3 className="text-xl font-bold text-gray-900">Add Property to Compare</h3>
            <p className="text-xs text-gray-500 mt-0.5">Search and select a property to add to your side-by-side matrix</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-200 transition-colors"
            aria-label="Close modal"
          >
            <XMarkIcon className="w-6 h-6" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-6 border-b border-gray-100 bg-white">
          <div className="relative">
            <MagnifyingGlassIcon className="w-5 h-5 absolute left-3.5 top-3.5 text-gray-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by property title, city, Patta, or Survey #..."
              className="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:bg-white text-sm outline-none transition-all"
              autoFocus
            />
          </div>
        </div>

        {/* Property List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-3">
          {isLoading ? (
            <div className="flex justify-center items-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : results.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <p className="text-base font-medium">No matching properties found.</p>
              <p className="text-xs text-gray-400 mt-1">Try refining your search keyword.</p>
            </div>
          ) : (
            results.map((p) => {
              const isAdded = currentPropertyIds.includes(p.id);
              return (
                <div
                  key={p.id}
                  className={`flex items-center gap-4 p-3 rounded-xl border transition-all ${
                    isAdded
                      ? 'border-primary-200 bg-primary-50/40 opacity-75'
                      : 'border-gray-200 hover:border-primary-400 hover:shadow-sm bg-white'
                  }`}
                >
                  {p.primary_image ? (
                    <img
                      src={p.primary_image}
                      alt={p.title}
                      className="w-16 h-16 object-cover rounded-lg flex-shrink-0"
                    />
                  ) : (
                    <div className="w-16 h-16 bg-gray-100 rounded-lg flex items-center justify-center text-2xl flex-shrink-0">
                      🏡
                    </div>
                  )}

                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-semibold text-gray-900 truncate">{p.title}</h4>
                    <p className="text-xs text-gray-500 truncate">
                      {p.city}, {p.state} • {p.total_area} {p.area_unit}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-sm font-bold text-primary-700">{formatPrice(p.price)}</span>
                      {p.verification_score >= 80 && (
                        <span className="text-[10px] bg-green-100 text-green-800 font-semibold px-2 py-0.5 rounded-full">
                          Verified
                        </span>
                      )}
                    </div>
                  </div>

                  <button
                    disabled={isAdded}
                    onClick={() => {
                      onSelectProperty(p.id);
                      onClose();
                    }}
                    className={`px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                      isAdded
                        ? 'bg-gray-200 text-gray-600 cursor-not-allowed'
                        : 'bg-primary-600 hover:bg-primary-700 text-white shadow-sm'
                    }`}
                  >
                    {isAdded ? (
                      <>
                        <CheckIcon className="w-4 h-4" /> Added
                      </>
                    ) : (
                      <>
                        <PlusIcon className="w-4 h-4" /> Add
                      </>
                    )}
                  </button>
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};

export default AddPropertyModal;
