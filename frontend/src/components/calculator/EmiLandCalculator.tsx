import React, { useState, useMemo } from 'react';
import {
  CalculatorIcon,
  ScaleIcon,
  CurrencyRupeeIcon,
  ChartPieIcon,
  ArrowPathIcon,
  InformationCircleIcon,
} from '@heroicons/react/24/outline';

interface EmiLandCalculatorProps {
  initialPrice?: number;
  initialArea?: number;
  initialAreaUnit?: string;
}

// Indian Land Conversion factors relative to Square Feet
const LAND_UNITS: Record<string, { name: string; sqftFactor: number; description: string }> = {
  sqft: { name: 'Square Feet (sq ft)', sqftFactor: 1, description: 'Standard metric for urban plots and building built-up area' },
  cent: { name: 'Cent', sqftFactor: 435.6, description: 'Widely used land metric in South India (1 Cent = 435.6 sq ft)' },
  ground: { name: 'Ground', sqftFactor: 2400, description: 'Traditional plot metric in Tamil Nadu (1 Ground = 2,400 sq ft)' },
  acre: { name: 'Acre', sqftFactor: 43560, description: 'Standard agricultural & large plot metric (1 Acre = 100 Cents)' },
  hectare: { name: 'Hectare', sqftFactor: 107639.1, description: 'Metric system unit (1 Hectare = 2.471 Acres)' },
  guntha: { name: 'Guntha', sqftFactor: 1089, description: 'Commonly used in Maharashtra, Gujarat & Karnataka (40 Gunthas = 1 Acre)' },
  bigha: { name: 'Bigha', sqftFactor: 27225, description: 'Traditional unit used across North & Central India' },
};

const EmiLandCalculator: React.FC<EmiLandCalculatorProps> = ({
  initialPrice = 5000000,
  initialArea = 1200,
  initialAreaUnit = 'sqft',
}) => {
  const [activeTab, setActiveTab] = useState<'emi' | 'converter'>('emi');

  // --- EMI CALCULATOR STATE ---
  const [propertyPrice, setPropertyPrice] = useState<number>(initialPrice);
  const [downPaymentPercent, setDownPaymentPercent] = useState<number>(20);
  const [interestRate, setInterestRate] = useState<number>(8.5);
  const [tenureYears, setTenureYears] = useState<number>(20);

  // --- LAND CONVERTER STATE ---
  const [inputValue, setInputValue] = useState<number>(initialArea);
  const [sourceUnit, setSourceUnit] = useState<string>(initialAreaUnit in LAND_UNITS ? initialAreaUnit : 'sqft');

  // --- EMI CALCULATIONS ---
  const emiMetrics = useMemo(() => {
    const downPayment = (propertyPrice * downPaymentPercent) / 100;
    const loanAmount = Math.max(0, propertyPrice - downPayment);
    const monthlyRate = interestRate / (12 * 100);
    const months = tenureYears * 12;

    if (loanAmount <= 0 || monthlyRate <= 0 || months <= 0) {
      return { downPayment: 0, loanAmount: 0, monthlyEmi: 0, totalInterest: 0, totalPayment: 0, principalPercent: 100, interestPercent: 0 };
    }

    const emi =
      (loanAmount * monthlyRate * Math.pow(1 + monthlyRate, months)) /
      (Math.pow(1 + monthlyRate, months) - 1);

    const totalPayment = emi * months;
    const totalInterest = totalPayment - loanAmount;

    const principalPercent = Math.round((loanAmount / totalPayment) * 100);
    const interestPercent = 100 - principalPercent;

    return {
      downPayment,
      loanAmount,
      monthlyEmi: Math.round(emi),
      totalInterest: Math.round(totalInterest),
      totalPayment: Math.round(totalPayment),
      principalPercent,
      interestPercent,
    };
  }, [propertyPrice, downPaymentPercent, interestRate, tenureYears]);

  // --- LAND CONVERSION CALCULATIONS ---
  const conversionMatrix = useMemo(() => {
    const sourceFactor = LAND_UNITS[sourceUnit]?.sqftFactor || 1;
    const valueInSqFt = inputValue * sourceFactor;

    return Object.entries(LAND_UNITS).map(([key, config]) => {
      const converted = valueInSqFt / config.sqftFactor;
      return {
        unitKey: key,
        name: config.name,
        value: converted < 0.01 ? converted.toFixed(4) : converted.toLocaleString(undefined, { maximumFractionDigits: 2 }),
        description: config.description,
      };
    });
  }, [inputValue, sourceUnit]);

  const formatCurrency = (val: number) => {
    if (val >= 10000000) return `₹${(val / 10000000).toFixed(2)} Cr`;
    if (val >= 100000) return `₹${(val / 100000).toFixed(2)} L`;
    return `₹${val.toLocaleString()}`;
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-md overflow-hidden">
      {/* Navigation Tabs */}
      <div className="flex border-b border-gray-200 bg-gray-50/80 p-1.5 gap-2">
        <button
          onClick={() => setActiveTab('emi')}
          className={`flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
            activeTab === 'emi'
              ? 'bg-white text-primary-700 shadow-sm border border-gray-200'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/50'
          }`}
        >
          <CalculatorIcon className="w-5 h-5 text-primary-600" />
          <span>Home Loan EMI Calculator</span>
        </button>

        <button
          onClick={() => setActiveTab('converter')}
          className={`flex-1 py-3 px-4 rounded-xl text-xs sm:text-sm font-bold flex items-center justify-center gap-2 transition-all ${
            activeTab === 'converter'
              ? 'bg-white text-primary-700 shadow-sm border border-gray-200'
              : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100/50'
          }`}
        >
          <ScaleIcon className="w-5 h-5 text-primary-600" />
          <span>Indian Land Area Unit Converter</span>
        </button>
      </div>

      {/* Tab 1: EMI Calculator */}
      {activeTab === 'emi' && (
        <div className="p-6 sm:p-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Controls Column */}
          <div className="lg:col-span-7 space-y-6">
            {/* Property Price */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700">Property Price</label>
                <span className="text-sm font-extrabold text-primary-700">{formatCurrency(propertyPrice)}</span>
              </div>
              <input
                type="number"
                value={propertyPrice}
                onChange={(e) => setPropertyPrice(Math.max(0, Number(e.target.value)))}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl text-sm font-bold text-gray-900 focus:ring-2 focus:ring-primary-500 focus:bg-white outline-none"
              />
              <input
                type="range"
                min="500000"
                max="50000000"
                step="100000"
                value={propertyPrice}
                onChange={(e) => setPropertyPrice(Number(e.target.value))}
                className="w-full mt-2 accent-primary-600 cursor-pointer"
              />
            </div>

            {/* Down Payment Percent */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700">Down Payment ({downPaymentPercent}%)</label>
                <span className="text-sm font-bold text-gray-900">{formatCurrency(emiMetrics.downPayment)}</span>
              </div>
              <input
                type="range"
                min="10"
                max="50"
                step="5"
                value={downPaymentPercent}
                onChange={(e) => setDownPaymentPercent(Number(e.target.value))}
                className="w-full accent-primary-600 cursor-pointer"
              />
              <div className="flex justify-between text-[11px] text-gray-400 mt-1 font-medium">
                <span>10% (Min)</span>
                <span>20% (Standard)</span>
                <span>50% (Max)</span>
              </div>
            </div>

            {/* Interest Rate */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700">Interest Rate (p.a.)</label>
                <span className="text-sm font-extrabold text-primary-700">{interestRate}%</span>
              </div>
              <input
                type="range"
                min="6.5"
                max="15.0"
                step="0.1"
                value={interestRate}
                onChange={(e) => setInterestRate(Number(e.target.value))}
                className="w-full accent-primary-600 cursor-pointer"
              />
            </div>

            {/* Loan Tenure */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700">Loan Tenure</label>
                <span className="text-sm font-extrabold text-primary-700">{tenureYears} Years</span>
              </div>
              <input
                type="range"
                min="1"
                max="30"
                step="1"
                value={tenureYears}
                onChange={(e) => setTenureYears(Number(e.target.value))}
                className="w-full accent-primary-600 cursor-pointer"
              />
            </div>
          </div>

          {/* Results Summary Column */}
          <div className="lg:col-span-5 bg-gradient-to-br from-primary-900 via-primary-800 to-primary-950 text-white rounded-2xl p-6 sm:p-8 flex flex-col justify-between shadow-xl">
            <div>
              <div className="flex items-center gap-2 mb-4 text-primary-200">
                <CurrencyRupeeIcon className="w-5 h-5" />
                <span className="text-xs font-bold uppercase tracking-wider">Estimated Monthly EMI</span>
              </div>

              <div className="text-3xl sm:text-4xl font-extrabold text-white mb-6 tracking-tight">
                ₹{emiMetrics.monthlyEmi.toLocaleString()} <span className="text-xs font-medium text-primary-300">/ month</span>
              </div>

              <div className="space-y-4 text-xs sm:text-sm border-t border-primary-700/60 pt-5">
                <div className="flex justify-between">
                  <span className="text-primary-200 font-medium">Principal Loan Amount</span>
                  <span className="font-bold text-white">{formatCurrency(emiMetrics.loanAmount)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-primary-200 font-medium">Total Interest Payable</span>
                  <span className="font-bold text-amber-300">{formatCurrency(emiMetrics.totalInterest)}</span>
                </div>
                <div className="flex justify-between border-t border-primary-700/60 pt-3">
                  <span className="text-primary-100 font-bold">Total Amount Payable</span>
                  <span className="font-extrabold text-white text-base">{formatCurrency(emiMetrics.totalPayment)}</span>
                </div>
              </div>
            </div>

            {/* Visual Breakdown Bar */}
            <div className="mt-8 pt-4 border-t border-primary-700/60">
              <div className="flex justify-between text-[11px] font-bold mb-2 text-primary-200">
                <span>Principal ({emiMetrics.principalPercent}%)</span>
                <span>Interest ({emiMetrics.interestPercent}%)</span>
              </div>
              <div className="h-3 w-full bg-primary-950 rounded-full overflow-hidden flex">
                <div className="h-full bg-emerald-400" style={{ width: `${emiMetrics.principalPercent}%` }} />
                <div className="h-full bg-amber-400" style={{ width: `${emiMetrics.interestPercent}%` }} />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Land Unit Converter */}
      {activeTab === 'converter' && (
        <div className="p-6 sm:p-8 space-y-6">
          {/* Input & Unit Selector Bar */}
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-4 bg-gray-50 p-4 rounded-xl border border-gray-200">
            <div className="sm:col-span-6">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5 block">Enter Land Measure</label>
              <input
                type="number"
                value={inputValue}
                onChange={(e) => setInputValue(Math.max(0, Number(e.target.value)))}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-base font-bold text-gray-900 focus:ring-2 focus:ring-primary-500 outline-none"
                placeholder="e.g. 2400"
              />
            </div>

            <div className="sm:col-span-6">
              <label className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-1.5 block">Source Unit</label>
              <select
                value={sourceUnit}
                onChange={(e) => setSourceUnit(e.target.value)}
                className="w-full px-4 py-3 bg-white border border-gray-300 rounded-xl text-sm font-bold text-gray-900 focus:ring-2 focus:ring-primary-500 outline-none cursor-pointer"
              >
                {Object.entries(LAND_UNITS).map(([key, config]) => (
                  <option key={key} value={key}>
                    {config.name}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Real-time Conversion Matrix Table */}
          <div className="overflow-x-auto rounded-xl border border-gray-200">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-primary-50 text-primary-900 text-xs font-bold uppercase tracking-wider border-b border-gray-200">
                  <th className="py-3 px-4">Target Unit</th>
                  <th className="py-3 px-4">Equivalent Value</th>
                  <th className="py-3 px-4 hidden md:table-cell">Standard Measurement Context</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {conversionMatrix.map((row) => (
                  <tr
                    key={row.unitKey}
                    className={`hover:bg-gray-50 transition-colors ${
                      row.unitKey === sourceUnit ? 'bg-primary-50/40 font-bold' : ''
                    }`}
                  >
                    <td className="py-3.5 px-4 text-sm font-semibold text-gray-900 flex items-center gap-2">
                      {row.unitKey === sourceUnit && <span className="text-primary-600 text-xs">●</span>}
                      {row.name}
                    </td>
                    <td className="py-3.5 px-4 text-base font-extrabold text-primary-700">
                      {row.value}
                    </td>
                    <td className="py-3.5 px-4 text-xs text-gray-500 hidden md:table-cell">
                      {row.description}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default EmiLandCalculator;
