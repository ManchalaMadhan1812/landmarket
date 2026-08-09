import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export const MAX_COMPARE = 4;

interface CompareState {
  propertyIds: string[]
  
  // Actions
  addProperty: (id: string) => void
  removeProperty: (id: string) => void
  clearComparison: () => void
  isComparing: (id: string) => boolean
}

export const useCompareStore = create<CompareState>()(
  persist(
    (set, get) => ({
      propertyIds: [],

      addProperty: (id: string) => {
        const currentIds = get().propertyIds;
        if (currentIds.length < MAX_COMPARE && !currentIds.includes(id)) {
          set({ propertyIds: [...currentIds, id] });
        }
      },

      removeProperty: (id: string) => {
        set({
          propertyIds: get().propertyIds.filter(existingId => existingId !== id)
        });
      },

      clearComparison: () => {
        set({ propertyIds: [] });
      },

      isComparing: (id: string) => {
        return get().propertyIds.includes(id);
      }
    }),
    {
      name: 'landmarket-compare',
    }
  )
)
