import React, { useState, useMemo } from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { useCompareStore, MAX_COMPARE } from '../stores/compareStore';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import AddPropertyModal from '../components/search/AddPropertyModal';
import { searchProperties } from '../services/searchService';
import {
  ArrowLeftIcon,
  PlusIcon,
  TrashIcon,
  ShareIcon,
  CheckCircleIcon,
  ShieldCheckIcon,
  SparklesIcon,
  MapPinIcon,
  DocumentCheckIcon,
  FunnelIcon,
  BuildingOfficeIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

const ComparePage: React.FC = () => {
  const { propertyIds, addProperty, removeProperty, clearComparison } = useCompareStore();
  const [onlyDifferences, setOnlyDifferences] = useState(false);
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);

  const { data, isLoading, error } = useQuery({
    queryKey: ['compare', propertyIds],
    queryFn: () => searchProperties({ ids: propertyIds }),
    enabled: propertyIds.length > 0,
  });

  const properties = data?.results || [];

  // Helper to format currency
  const formatPrice = (price: number) => {
    if (price >= 10000000) {
      return `₹${(price / 10000000).toFixed(2)} Cr`;
    } else if (price >= 100000) {
      return `₹${(price / 100000).toFixed(2)} L`;
    }
    return `₹${price.toLocaleString()}`;
  };

  // Dynamically calculate "Winner / Best" badges across compared properties
  const metricsWinners = useMemo(() => {
    if (!properties || properties.length < 2) return {};

    let lowestPriceId = properties[0].id;
    let highestScoreId = properties[0].id;
    let largestAreaId = properties[0].id;

    properties.forEach((p) => {
      if (p.price < properties.find((item) => item.id === lowestPriceId)!.price) {
        lowestPriceId = p.id;
      }
      if (p.verification_score > properties.find((item) => item.id === highestScoreId)!.verification_score) {
        highestScoreId = p.id;
      }
      if (p.total_area > properties.find((item) => item.id === largestAreaId)!.total_area) {
        largestAreaId = p.id;
      }
    });

    return { lowestPriceId, highestScoreId, largestAreaId };
  }, [properties]);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      toast.success('Comparison link copied to clipboard!');
    }
  };

  if (propertyIds.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="text-center bg-white p-8 rounded-2xl shadow-sm border border-gray-200 max-w-md w-full">
          <div className="w-16 h-16 bg-primary-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <BuildingOfficeIcon className="w-8 h-8 text-primary-600" />
          </div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Properties Selected</h2>
          <p className="text-gray-600 text-sm mb-6">
            Select up to 4 properties from search results or property pages to compare them side-by-side.
          </p>
          <Link to="/search" className="btn-primary inline-flex items-center gap-2 py-3 px-6 rounded-xl">
            Explore Properties to Compare
          </Link>
        </div>
      </div>
    );
  }

  // Row renderer with difference detection logic
  const renderRow = (
    label: string,
    getValue: (p: any) => React.ReactNode,
    getRawValue?: (p: any) => any,
    icon?: React.ReactNode
  ) => {
    if (onlyDifferences && getRawValue && properties.length > 1) {
      const firstVal = getRawValue(properties[0]);
      const allSame = properties.every((p) => getRawValue(p) === firstVal);
      if (allSame) return null;
    }

    return (
      <tr className="border-b border-gray-200 hover:bg-gray-50/50 transition-colors">
        <td className="py-4 px-4 font-semibold text-gray-900 bg-gray-50/80 w-52 sticky left-0 z-10 text-sm border-r border-gray-200 flex items-center gap-2">
          {icon}
          <span>{label}</span>
        </td>
        {properties.map((p) => (
          <td key={p.id} className="py-4 px-5 text-gray-700 text-sm min-w-[260px] max-w-[300px] border-r border-gray-100 last:border-r-0">
            {getValue(p)}
          </td>
        ))}
        {/* Fill remaining empty columns if < 4 */}
        {Array.from({ length: MAX_COMPARE - properties.length }).map((_, idx) => (
          <td key={`empty-cell-${idx}`} className="py-4 px-5 min-w-[260px] bg-gray-50/30 border-r border-gray-100 last:border-r-0" />
        ))}
      </tr>
    );
  };

  const renderSectionHeader = (title: string, icon?: React.ReactNode) => (
    <tr className="bg-primary-50/60 border-y border-primary-100">
      <td colSpan={MAX_COMPARE + 1} className="py-3 px-4 text-xs font-bold uppercase tracking-wider text-primary-900 sticky left-0 z-10 flex items-center gap-2">
        {icon}
        <span>{title}</span>
      </td>
    </tr>
  );

  return (
    <>
      <Helmet>
        <title>Side-by-Side Property Comparison - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header Controls */}
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8 bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
            <div className="flex items-center gap-4">
              <Link
                to="/search"
                className="p-2.5 bg-gray-100 hover:bg-gray-200 rounded-xl transition-colors text-gray-700"
                title="Back to search"
              >
                <ArrowLeftIcon className="w-5 h-5" />
              </Link>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">Side-by-Side Property Comparison</h1>
                <p className="text-xs sm:text-sm text-gray-500 mt-1">
                  Comparing <span className="font-semibold text-primary-700">{properties.length}</span> of {MAX_COMPARE} properties
                </p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              {/* Highlight Differences Toggle */}
              <label className="flex items-center gap-2 bg-gray-50 px-3.5 py-2 rounded-xl border border-gray-200 cursor-pointer hover:bg-gray-100 transition-colors text-xs font-medium text-gray-700">
                <input
                  type="checkbox"
                  checked={onlyDifferences}
                  onChange={(e) => setOnlyDifferences(e.target.checked)}
                  className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                />
                <FunnelIcon className="w-4 h-4 text-gray-500" />
                <span>Show Differences Only</span>
              </label>

              {/* Share Link */}
              <button
                onClick={handleShare}
                className="flex items-center gap-1.5 px-3.5 py-2 bg-gray-50 hover:bg-gray-100 text-gray-700 border border-gray-200 rounded-xl text-xs font-medium transition-colors"
              >
                <ShareIcon className="w-4 h-4" />
                <span>Share</span>
              </button>

              {/* Add Property Button */}
              {properties.length < MAX_COMPARE && (
                <button
                  onClick={() => setIsAddModalOpen(true)}
                  className="flex items-center gap-1.5 px-3.5 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors"
                >
                  <PlusIcon className="w-4 h-4" />
                  <span>Add Property</span>
                </button>
              )}

              {/* Clear All */}
              <button
                onClick={clearComparison}
                className="flex items-center gap-1.5 px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-xl text-xs font-medium transition-colors"
              >
                <TrashIcon className="w-4 h-4" />
                <span>Clear All</span>
              </button>
            </div>
          </div>

          {/* Loading or Matrix Content */}
          {isLoading ? (
            <div className="bg-white rounded-2xl p-12 flex justify-center items-center shadow-sm border border-gray-200 min-h-[400px]">
              <LoadingSpinner size="lg" />
            </div>
          ) : error ? (
            <div className="bg-red-50 border border-red-200 text-red-700 p-6 rounded-2xl">
              Failed to load comparison properties. Please try again.
            </div>
          ) : (
            <div className="bg-white rounded-2xl shadow-sm border border-gray-200 overflow-x-auto">
              <table className="w-full text-left border-collapse min-w-[700px]">
                {/* Table Header: Cards */}
                <thead>
                  <tr className="border-b border-gray-200 bg-gray-50/50">
                    <th className="p-4 bg-gray-50/90 sticky left-0 z-20 w-52 border-r border-gray-200 text-xs font-bold text-gray-500 uppercase tracking-wider">
                      Property Attributes
                    </th>
                    {properties.map((p) => {
                      const isLowestPrice = metricsWinners.lowestPriceId === p.id;
                      const isHighestScore = metricsWinners.highestScoreId === p.id;
                      const isLargestArea = metricsWinners.largestAreaId === p.id;

                      return (
                        <th key={p.id} className="p-5 min-w-[260px] max-w-[300px] align-top border-r border-gray-200 last:border-r-0 bg-white">
                          <div className="relative group">
                            {/* Remove button */}
                            <button
                              onClick={() => removeProperty(p.id)}
                              className="absolute -top-2 -right-2 bg-white text-gray-400 hover:text-red-500 hover:bg-red-50 p-1.5 rounded-full shadow-md border border-gray-200 transition-colors z-10"
                              title="Remove property"
                            >
                              <TrashIcon className="w-4 h-4" />
                            </button>

                            {/* Property Image & Badges */}
                            <div className="relative h-44 mb-3 rounded-xl overflow-hidden bg-gray-100 border border-gray-200">
                              {p.primary_image ? (
                                <img src={p.primary_image} alt={p.title} className="w-full h-full object-cover" />
                              ) : (
                                <div className="w-full h-full flex items-center justify-center text-4xl">🏠</div>
                              )}

                              <div className="absolute top-2 left-2 flex flex-col gap-1">
                                {isLowestPrice && (
                                  <span className="bg-emerald-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-md shadow flex items-center gap-1">
                                    <SparklesIcon className="w-3 h-3" /> Best Price
                                  </span>
                                )}
                                {isHighestScore && (
                                  <span className="bg-blue-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-md shadow flex items-center gap-1">
                                    <ShieldCheckIcon className="w-3 h-3" /> Top Verified
                                  </span>
                                )}
                                {isLargestArea && (
                                  <span className="bg-purple-600 text-white text-[10px] font-bold px-2 py-0.5 rounded-md shadow flex items-center gap-1">
                                    📐 Largest Plot
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Title & Price */}
                            <Link to={`/property/${p.id}`} className="text-base font-bold text-gray-900 hover:text-primary-600 line-clamp-2 mb-1.5 block">
                              {p.title}
                            </Link>

                            <div className="text-xl font-extrabold text-primary-700 mb-3">
                              {formatPrice(p.price)}
                            </div>

                            <Link
                              to={`/property/${p.id}`}
                              className="w-full py-2 px-3 bg-primary-50 hover:bg-primary-100 text-primary-700 text-xs font-semibold rounded-lg block text-center transition-colors mb-2"
                            >
                              View Full Details
                            </Link>
                          </div>
                        </th>
                      );
                    })}

                    {/* Empty Slots to Add Property */}
                    {Array.from({ length: MAX_COMPARE - properties.length }).map((_, idx) => (
                      <th key={`empty-slot-${idx}`} className="p-5 min-w-[260px] align-middle border-r border-gray-200 last:border-r-0 bg-gray-50/30">
                        <div
                          onClick={() => setIsAddModalOpen(true)}
                          className="h-64 border-2 border-dashed border-gray-300 rounded-xl flex flex-col items-center justify-center p-6 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/20 transition-all group"
                        >
                          <div className="w-12 h-12 rounded-full bg-white shadow border border-gray-200 flex items-center justify-center text-primary-600 group-hover:scale-110 transition-transform mb-3">
                            <PlusIcon className="w-6 h-6" />
                          </div>
                          <span className="text-sm font-bold text-gray-700 group-hover:text-primary-600">Add Property</span>
                          <span className="text-xs text-gray-400 mt-1">Slot {properties.length + idx + 1} of {MAX_COMPARE}</span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>

                {/* Categorized Rows */}
                <tbody>
                  {/* Overview Section */}
                  {renderSectionHeader('Pricing & Overview', <BuildingOfficeIcon className="w-4 h-4" />)}
                  {renderRow('Listing Type', (p) => <span className="capitalize font-medium">{p.property_type}</span>, (p) => p.property_type)}
                  {renderRow('Purpose', (p) => (
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold uppercase ${
                      p.purpose === 'sale' ? 'bg-green-100 text-green-800' :
                      p.purpose === 'rent' ? 'bg-blue-100 text-blue-800' : 'bg-purple-100 text-purple-800'
                    }`}>
                      {p.purpose}
                    </span>
                  ), (p) => p.purpose)}
                  {renderRow('Location', (p) => (
                    <span className="flex items-center gap-1 font-medium text-gray-800">
                      <MapPinIcon className="w-4 h-4 text-gray-400 flex-shrink-0" />
                      {p.city}, {p.state}
                    </span>
                  ), (p) => `${p.city}, ${p.state}`)}

                  {/* Land & Legal Records */}
                  {renderSectionHeader('Land Specs & Legal Documents', <DocumentCheckIcon className="w-4 h-4" />)}
                  {renderRow('Total Area', (p) => (
                    <span className="font-bold text-gray-900">
                      {p.total_area} {p.area_unit}
                    </span>
                  ), (p) => `${p.total_area} ${p.area_unit}`)}
                  {renderRow('Patta Number', (p) => (
                    p.patta_number ? (
                      <span className="inline-flex items-center gap-1 font-mono text-xs bg-emerald-50 text-emerald-800 border border-emerald-200 px-2 py-1 rounded-md">
                        <CheckCircleIcon className="w-3.5 h-3.5 text-emerald-600" /> {p.patta_number}
                      </span>
                    ) : <span className="text-gray-400 italic">Not Provided</span>
                  ), (p) => p.patta_number || '')}
                  {renderRow('Chitta Number', (p) => (
                    p.chitta_number ? (
                      <span className="font-mono text-xs bg-blue-50 text-blue-800 border border-blue-200 px-2 py-1 rounded-md">
                        {p.chitta_number}
                      </span>
                    ) : <span className="text-gray-400 italic">Not Provided</span>
                  ), (p) => p.chitta_number || '')}
                  {renderRow('Survey Number', (p) => (
                    p.survey_number ? (
                      <span className="font-mono text-xs bg-gray-100 text-gray-800 px-2 py-1 rounded-md">
                        {p.survey_number}
                      </span>
                    ) : <span className="text-gray-400 italic">Not Provided</span>
                  ), (p) => p.survey_number || '')}
                  {renderRow('RERA Status', (p) => (
                    p.rera_number ? (
                      <span className="text-xs bg-green-100 text-green-800 font-semibold px-2 py-1 rounded-md flex items-center gap-1 w-fit">
                        <ShieldCheckIcon className="w-3.5 h-3.5" /> Registered ({p.rera_number})
                      </span>
                    ) : <span className="text-gray-400 italic">Unregistered / N/A</span>
                  ), (p) => p.rera_number || '')}

                  {/* Trust & Engagement */}
                  {renderSectionHeader('Trust & Community Ratings', <ShieldCheckIcon className="w-4 h-4" />)}
                  {renderRow('Trust Score', (p) => (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-xs">
                        <span className={`font-bold ${p.verification_score >= 80 ? 'text-green-600' : 'text-yellow-600'}`}>
                          {p.verification_score}%
                        </span>
                        {p.verification_score >= 80 && (
                          <span className="text-[10px] bg-green-100 text-green-800 font-bold px-1.5 py-0.5 rounded">Verified</span>
                        )}
                      </div>
                      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div
                          className={`h-full ${p.verification_score >= 80 ? 'bg-green-500' : 'bg-yellow-500'}`}
                          style={{ width: `${p.verification_score}%` }}
                        />
                      </div>
                    </div>
                  ), (p) => p.verification_score)}
                  {renderRow('User Rating', (p) => (
                    p.avg_rating > 0 ? (
                      <span className="font-bold text-yellow-600 flex items-center gap-1">
                        ★ {p.avg_rating.toFixed(1)} <span className="text-xs text-gray-500 font-normal">/ 5.0</span>
                      </span>
                    ) : <span className="text-gray-400 text-xs">No ratings yet</span>
                  ), (p) => p.avg_rating)}
                  {renderRow('Popularity', (p) => (
                    <span className="text-xs text-gray-600">
                      👁️ {p.view_count} views • ❤️ {p.save_count} saves
                    </span>
                  ), (p) => `${p.view_count}-${p.save_count}`)}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Add Property Selection Modal */}
      <AddPropertyModal
        isOpen={isAddModalOpen}
        onClose={() => setIsAddModalOpen(false)}
        onSelectProperty={(id) => addProperty(id)}
        currentPropertyIds={propertyIds}
      />
    </>
  );
};

export default ComparePage;
