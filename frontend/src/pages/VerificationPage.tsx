import React from 'react';
import { Helmet } from 'react-helmet-async';
import { Link } from 'react-router-dom';
import DocumentVerificationSystem from '../components/verification/DocumentVerificationSystem';
import { ShieldCheckIcon, ArrowLeftIcon, SparklesIcon, QuestionMarkCircleIcon } from '@heroicons/react/24/outline';

const VerificationPage: React.FC = () => {
  return (
    <>
      <Helmet>
        <title>Property Verification & Legal Compliance - LandMarket</title>
      </Helmet>

      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Link
              to="/search"
              className="p-2.5 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 text-gray-700 shadow-sm transition-colors"
            >
              <ArrowLeftIcon className="w-5 h-5" />
            </Link>
            <div>
              <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary-700 mb-1">
                <SparklesIcon className="w-4 h-4" />
                <span>Legal Trust & Due Diligence</span>
              </div>
              <h1 className="text-3xl font-extrabold text-gray-900">Property Legal Verification System</h1>
            </div>
          </div>

          {/* Verification Widget Component */}
          <DocumentVerificationSystem />

          {/* Legal FAQ Section */}
          <div className="bg-white rounded-2xl border border-gray-200 p-6 sm:p-8 shadow-sm">
            <div className="flex items-center gap-2 mb-4 text-gray-900 font-bold text-lg border-b border-gray-100 pb-3">
              <QuestionMarkCircleIcon className="w-5 h-5 text-primary-600" />
              <span>Frequently Asked Questions About Indian Land Verification</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-xs sm:text-sm text-gray-600">
              <div className="space-y-1">
                <h4 className="font-bold text-gray-900">What is a Patta and why is it mandatory?</h4>
                <p>
                  A Patta is an official revenue document issued by the government in the name of the legal owner. It proves legal title and possession of land plots.
                </p>
              </div>

              <div className="space-y-1">
                <h4 className="font-bold text-gray-900">What does a 30-Year Encumbrance Certificate (EC) verify?</h4>
                <p>
                  The Encumbrance Certificate confirms whether there are any registered mortgages, liens, or legal disputes on the property over the last 30 years.
                </p>
              </div>

              <div className="space-y-1">
                <h4 className="font-bold text-gray-900">What is Chitta and FMB Sketch?</h4>
                <p>
                  Chitta describes land classification (wet/dry plot) while Field Measurement Book (FMB) sketch outlines exact boundary dimensions and road frontage.
                </p>
              </div>

              <div className="space-y-1">
                <h4 className="font-bold text-gray-900">How long does legal verification audit take?</h4>
                <p>
                  Once documents are submitted, our legal audit team verifies them with Sub-Registrar Office (SRO) records within 24 to 48 hours.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default VerificationPage;
