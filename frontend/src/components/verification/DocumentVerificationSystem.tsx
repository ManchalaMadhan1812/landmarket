import React, { useState, useMemo } from 'react';
import {
  DocumentCheckIcon,
  ShieldCheckIcon,
  ExclamationTriangleIcon,
  ArrowUpTrayIcon,
  CheckCircleIcon,
  ClockIcon,
  XCircleIcon,
  DocumentTextIcon,
  EyeIcon,
  XMarkIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

export interface LandDocument {
  id: string;
  type: 'patta' | 'chitta' | 'ec' | 'title_deed' | 'rera' | 'survey_sketch';
  title: string;
  weight: number;
  status: 'verified' | 'under_review' | 'action_required' | 'not_uploaded';
  documentNumber?: string;
  issueDate?: string;
  verifiedBy?: string;
  fileUrl?: string;
  notes?: string;
}

const INITIAL_DOCUMENTS: LandDocument[] = [
  {
    id: 'doc-1',
    type: 'patta',
    title: 'Patta (Land Revenue & Ownership Record)',
    weight: 25,
    status: 'verified',
    documentNumber: 'PATTA-TN-2025-8892',
    issueDate: '2025-01-15',
    verifiedBy: 'SRO Chengalpattu / Legal Audit Team',
    notes: 'Ownership clear. Revenue records match current vendor name.',
  },
  {
    id: 'doc-2',
    type: 'chitta',
    title: 'Chitta (Land Classification & Area Details)',
    weight: 20,
    status: 'verified',
    documentNumber: 'CHITTA-882910',
    issueDate: '2025-01-18',
    verifiedBy: 'SRO Chengalpattu',
    notes: 'Wet/Dry classification verified as Nanjai/Punjai plot.',
  },
  {
    id: 'doc-3',
    type: 'ec',
    title: 'Encumbrance Certificate (30-Year EC)',
    weight: 20,
    status: 'verified',
    documentNumber: 'EC-30Y-2025-00129',
    issueDate: '2025-02-01',
    verifiedBy: 'Sub-Registrar Office',
    notes: 'Zero encumbrances found for past 30 years. No active mortgages.',
  },
  {
    id: 'doc-4',
    type: 'title_deed',
    title: 'Parent Title Deed / Sale Deed',
    weight: 15,
    status: 'under_review',
    documentNumber: 'DEED-2018-4491',
    issueDate: '2018-06-12',
    notes: 'Submitted for verification of chain of title documents.',
  },
  {
    id: 'doc-5',
    type: 'rera',
    title: 'RERA Registration Certificate',
    weight: 10,
    status: 'action_required',
    notes: 'Please upload updated RERA certificate or exemption letter.',
  },
  {
    id: 'doc-6',
    type: 'survey_sketch',
    title: 'FMB / Survey Sketch Map',
    weight: 10,
    status: 'not_uploaded',
    notes: 'Upload FMB sketch map showing exact plot boundary lines.',
  },
];

const DocumentVerificationSystem: React.FC = () => {
  const [documents, setDocuments] = useState<LandDocument[]>(INITIAL_DOCUMENTS);
  const [activeUploadDoc, setActiveUploadDoc] = useState<LandDocument | null>(null);
  const [uploadDocNum, setUploadDocNum] = useState('');
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  // Dynamic Trust Score Calculation
  const trustScore = useMemo(() => {
    return documents.reduce((acc, doc) => {
      if (doc.status === 'verified') return acc + doc.weight;
      if (doc.status === 'under_review') return acc + Math.round(doc.weight * 0.5);
      return acc;
    }, 0);
  }, [documents]);

  const handleOpenUpload = (doc: LandDocument) => {
    setActiveUploadDoc(doc);
    setUploadDocNum(doc.documentNumber || '');
    setUploadFile(null);
  };

  const handleUploadSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!activeUploadDoc) return;

    setDocuments((prev) =>
      prev.map((d) =>
        d.id === activeUploadDoc.id
          ? {
              ...d,
              status: 'under_review',
              documentNumber: uploadDocNum || `DOC-${Math.floor(100000 + Math.random() * 900000)}`,
              notes: 'Document submitted successfully. Verification under review by legal team.',
            }
          : d
      )
    );

    toast.success(`${activeUploadDoc.title} uploaded for legal review!`);
    setActiveUploadDoc(null);
  };

  const getStatusBadge = (status: LandDocument['status']) => {
    switch (status) {
      case 'verified':
        return (
          <span className="inline-flex items-center gap-1 bg-green-100 text-green-800 text-xs font-bold px-2.5 py-1 rounded-full">
            <CheckCircleIcon className="w-4 h-4 text-green-600" />
            <span>Verified</span>
          </span>
        );
      case 'under_review':
        return (
          <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-xs font-bold px-2.5 py-1 rounded-full">
            <ClockIcon className="w-4 h-4 text-blue-600" />
            <span>Under Review</span>
          </span>
        );
      case 'action_required':
        return (
          <span className="inline-flex items-center gap-1 bg-amber-100 text-amber-800 text-xs font-bold px-2.5 py-1 rounded-full">
            <ExclamationTriangleIcon className="w-4 h-4 text-amber-600" />
            <span>Action Required</span>
          </span>
        );
      case 'not_uploaded':
        return (
          <span className="inline-flex items-center gap-1 bg-gray-100 text-gray-600 text-xs font-medium px-2.5 py-1 rounded-full">
            <XCircleIcon className="w-4 h-4 text-gray-400" />
            <span>Not Uploaded</span>
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-gray-200 shadow-sm overflow-hidden">
      {/* Header Banner & Trust Score Card */}
      <div className="bg-gradient-to-r from-gray-900 via-primary-950 to-gray-900 text-white p-6 sm:p-8">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div>
            <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-primary-300 mb-1">
              <ShieldCheckIcon className="w-5 h-5 text-primary-400" />
              <span>Legal Compliance & Document Verification Engine</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-white">Land Legal Trust & Verification Status</h2>
            <p className="text-xs sm:text-sm text-gray-300 mt-1 max-w-xl">
              Inspect verified Patta, Chitta, 30-Year Encumbrance Certificate (EC), and RERA documents for legal safety.
            </p>
          </div>

          {/* Trust Score Gauge Card */}
          <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-2xl p-5 min-w-[240px] text-center shadow-lg">
            <div className="text-xs font-bold uppercase tracking-wider text-primary-200 mb-1">Overall Trust Score</div>
            <div className="text-4xl font-extrabold text-white mb-2 flex items-center justify-center gap-1">
              <span>{trustScore}%</span>
              {trustScore >= 80 && <SparklesIcon className="w-6 h-6 text-amber-300" />}
            </div>

            <div className="w-full bg-white/20 h-2.5 rounded-full overflow-hidden mb-2">
              <div
                className={`h-full transition-all duration-500 ${
                  trustScore >= 80 ? 'bg-emerald-400' : trustScore >= 50 ? 'bg-amber-400' : 'bg-red-400'
                }`}
                style={{ width: `${trustScore}%` }}
              />
            </div>

            <span className="text-[11px] font-semibold text-primary-100">
              {trustScore >= 80 ? 'Fully Verified & Safe' : trustScore >= 50 ? 'Partially Verified' : 'Action Needed'}
            </span>
          </div>
        </div>
      </div>

      {/* Document Checklist List */}
      <div className="p-6 sm:p-8 space-y-4">
        <div className="flex items-center justify-between border-b border-gray-200 pb-3">
          <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
            <DocumentCheckIcon className="w-5 h-5 text-primary-600" />
            <span>Required Legal Document Checklist ({documents.filter((d) => d.status === 'verified').length} / {documents.length} Verified)</span>
          </h3>
        </div>

        <div className="grid grid-cols-1 gap-4">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className={`p-5 rounded-2xl border transition-all ${
                doc.status === 'verified'
                  ? 'border-green-200 bg-green-50/20'
                  : doc.status === 'under_review'
                  ? 'border-blue-200 bg-blue-50/20'
                  : doc.status === 'action_required'
                  ? 'border-amber-200 bg-amber-50/20'
                  : 'border-gray-200 bg-gray-50/40'
              }`}
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="space-y-1">
                  <div className="flex items-center gap-3">
                    <h4 className="text-base font-bold text-gray-900">{doc.title}</h4>
                    {getStatusBadge(doc.status)}
                  </div>

                  {doc.documentNumber && (
                    <div className="text-xs font-mono text-gray-600">
                      Doc #: <span className="font-bold text-gray-900">{doc.documentNumber}</span>
                      {doc.issueDate && <span className="ml-3 text-gray-500">Issued: {doc.issueDate}</span>}
                    </div>
                  )}

                  {doc.notes && <p className="text-xs text-gray-600 italic mt-1">"{doc.notes}"</p>}
                </div>

                <div className="flex items-center gap-2">
                  {doc.status === 'verified' && (
                    <button
                      onClick={() => toast.success(`Viewing verified ${doc.title}`)}
                      className="px-3 py-2 bg-white hover:bg-gray-50 border border-gray-200 rounded-xl text-xs font-semibold text-gray-700 flex items-center gap-1.5 shadow-sm transition-colors"
                    >
                      <EyeIcon className="w-4 h-4 text-gray-500" />
                      <span>View Verified Doc</span>
                    </button>
                  )}

                  {(doc.status === 'not_uploaded' || doc.status === 'action_required' || doc.status === 'under_review') && (
                    <button
                      onClick={() => handleOpenUpload(doc)}
                      className="px-3.5 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-colors"
                    >
                      <ArrowUpTrayIcon className="w-4 h-4" />
                      <span>{doc.status === 'under_review' ? 'Re-upload / Update' : 'Upload Document'}</span>
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Upload Modal Dialog */}
      {activeUploadDoc && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-5 animate-fade-in">
            <div className="flex items-center justify-between border-b border-gray-200 pb-3">
              <div>
                <h3 className="text-lg font-bold text-gray-900">Upload {activeUploadDoc.title}</h3>
                <p className="text-xs text-gray-500 mt-0.5">Submit official document for legal verification audit</p>
              </div>
              <button
                onClick={() => setActiveUploadDoc(null)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              >
                <XMarkIcon className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleUploadSubmit} className="space-y-4">
              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-1 block">Document / Reference Number</label>
                <input
                  type="text"
                  value={uploadDocNum}
                  onChange={(e) => setUploadDocNum(e.target.value)}
                  placeholder="e.g. PATTA-TN-2025-1029"
                  className="w-full px-4 py-2.5 bg-gray-50 border border-gray-300 rounded-xl text-sm font-semibold focus:ring-2 focus:ring-primary-500 focus:bg-white outline-none"
                  required
                />
              </div>

              <div>
                <label className="text-xs font-bold uppercase tracking-wider text-gray-700 mb-1 block">Select File (PDF, JPG, PNG)</label>
                <div className="border-2 border-dashed border-gray-300 rounded-xl p-6 text-center bg-gray-50 hover:bg-gray-100/50 cursor-pointer transition-colors">
                  <DocumentTextIcon className="w-10 h-10 text-gray-400 mx-auto mb-2" />
                  <p className="text-xs font-medium text-gray-700">Click to browse or drop document file here</p>
                  <p className="text-[10px] text-gray-400 mt-1">Supports PDF, PNG, WEBP (Max 15MB)</p>
                  <input
                    type="file"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    className="hidden"
                    id="doc-file-input"
                  />
                  <label htmlFor="doc-file-input" className="mt-3 inline-block px-3 py-1.5 bg-white border border-gray-300 text-xs font-bold text-gray-700 rounded-lg shadow-sm cursor-pointer hover:bg-gray-50">
                    {uploadFile ? uploadFile.name : 'Choose File'}
                  </label>
                </div>
              </div>

              <div className="flex gap-2 pt-2">
                <button
                  type="button"
                  onClick={() => setActiveUploadDoc(null)}
                  className="flex-1 py-2.5 px-4 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl text-xs font-semibold transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-xl text-xs font-semibold shadow-md transition-colors"
                >
                  Submit for Verification
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentVerificationSystem;
