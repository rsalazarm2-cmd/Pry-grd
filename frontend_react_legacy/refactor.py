import os
import shutil
import re
from pathlib import Path

def main():
    base_dir = Path.cwd()
    src_dir = base_dir / 'src'
    
    # 1. Create domains
    domains = ['bronze', 'silver', 'gold', 'project', 'shared']
    for d in domains:
        (src_dir / d).mkdir(exist_ok=True)
    
    # 2. File Mappings (Source relative to src -> Target relative to src)
    mappings = {
        # Bronze
        "components/bronze/BronzeWorkspace.tsx": "bronze/components/BronzeWorkspace.tsx",
        "components/cleaning": "bronze/components/cleaning",
        "components/tables/BronzeTable.tsx": "bronze/components/tables/BronzeTable.tsx",
        "components/tables/BronzeProfilingDiagnostic.tsx": "bronze/components/tables/BronzeProfilingDiagnostic.tsx",
        "hooks/useCleaningRules.ts": "bronze/hooks/useCleaningRules.ts",
        
        # Silver
        "components/silver": "silver/components",
        "components/tables/SilverTable.tsx": "silver/components/tables/SilverTable.tsx",
        "components/tables/SilverProfilingDiagnostic.tsx": "silver/components/tables/SilverProfilingDiagnostic.tsx",
        "api/atomicityApi.ts": "silver/api/atomicityApi.ts",
        
        # Gold
        "components/gold": "gold/components",
        "components/tables/GoldAccountTable.tsx": "gold/components/tables/GoldAccountTable.tsx",
        "components/tables/GoldLedgerTable.tsx": "gold/components/tables/GoldLedgerTable.tsx",
        
        # Project
        "components/projects": "project/components",
        "components/ProjectSelectorModal.tsx": "project/components/ProjectSelectorModal.tsx",
        "components/layout/EmptyProjectState.tsx": "project/components/layout/EmptyProjectState.tsx",
        "api/projectApi.ts": "project/api/projectApi.ts",
        
        # Shared
        "api/client.ts": "shared/api/client.ts",
        "api/httpClient.ts": "shared/api/httpClient.ts",
        "api/medallionApi.ts": "shared/api/medallionApi.ts",
        "api/types.ts": "shared/api/types.ts",
        "hooks/useMedallionQueries.ts": "shared/hooks/useMedallionQueries.ts",
        "hooks/useMedallionState.ts": "shared/hooks/useMedallionState.ts",
        "store": "shared/store",
        "components/common": "shared/components/common",
        "components/ExcelColumnFilter.tsx": "shared/components/ExcelColumnFilter.tsx",
        "components/tables/ExcelColumnFilter.tsx": "shared/components/tables/ExcelColumnFilter.tsx",
        "components/layout/Header.tsx": "shared/components/layout/Header.tsx",
        "components/layout/KpiCards.tsx": "shared/components/layout/KpiCards.tsx",
        "components/layout/TabNavigation.tsx": "shared/components/layout/TabNavigation.tsx",
        "utils": "shared/utils",
    }
    
    # Track file movements for import updates
    file_moves = {}
    
    for src_rel, tgt_rel in mappings.items():
        src_path = src_dir / src_rel
        tgt_path = src_dir / tgt_rel
        if src_path.exists():
            tgt_path.parent.mkdir(parents=True, exist_ok=True)
            if src_path.is_dir():
                # Store all nested files in file_moves
                for root, _, files in os.walk(src_path):
                    for f in files:
                        old_p = Path(root) / f
                        rel_to_src = old_p.relative_to(src_dir)
                        # Re-calculate target based on directory mapping
                        rel_to_dir = old_p.relative_to(src_path)
                        new_p = tgt_path / rel_to_dir
                        file_moves[str(rel_to_src)] = str(new_p.relative_to(src_dir))
                shutil.move(str(src_path), str(tgt_path))
            else:
                file_moves[str(src_rel)] = str(tgt_rel)
                shutil.move(str(src_path), str(tgt_path))

    # Optional: Delete empty directories
    for p in [src_dir / 'components/tables', src_dir / 'components/layout', src_dir / 'components', src_dir / 'api', src_dir / 'hooks']:
        if p.exists() and not os.listdir(p):
            p.rmdir()
            
    print(f"Moved {len(file_moves)} files.")
    
    # 3. Update imports in all .ts and .tsx files
    # We will use absolute-like imports if they start with @/ or relative imports.
    # In Vite, usually aliases like `@/` or relative `../../` are used.
    # Since I don't know if aliases are configured, I will just convert everything to absolute `src/...` if I can, or adjust relative paths.
    
    # Wait, the frontend is currently using relative imports everywhere! 
    # Let's fix relative imports.
    
    # Function to calculate new relative import
    def get_new_relative_path(from_file, to_file):
        from_dir = Path(from_file).parent
        to_path = Path(to_file)
        
        rel = os.path.relpath(to_path, from_dir)
        if not rel.startswith('.'):
            rel = './' + rel
        
        # Remove extension (.ts, .tsx)
        if rel.endswith('.tsx'):
            rel = rel[:-4]
        elif rel.endswith('.ts'):
            rel = rel[:-3]
            
        return rel

    # Let's just do a naive pass over all TS/TSX files and regex replace
    all_ts_files = list(src_dir.rglob("*.ts")) + list(src_dir.rglob("*.tsx"))
    
    # Map old absolute-ish paths (like 'components/bronze/BronzeWorkspace') to new relative paths.
    for file_path in all_ts_files:
        content = file_path.read_text()
        new_content = content
        
        file_rel_to_src = str(file_path.relative_to(src_dir))
        
        # We need to find all import statements
        # import { X } from '../../components/tables/BronzeTable'
        import_pattern = re.compile(r'(import\s+.*?from\s+[\'"])(.*?)([\'"])', re.MULTILINE | re.DOTALL)
        
        def replace_import(match):
            prefix = match.group(1)
            import_path = match.group(2)
            suffix = match.group(3)
            
            # If it's a relative path or absolute path
            if import_path.startswith('.'):
                # Resolve it to old src-relative path
                # Because the file content currently has imports based on its NEW location? 
                # No, the file content has imports based on its OLD location.
                
                # We need to find the OLD location of this file
                old_file_rel = None
                for k, v in file_moves.items():
                    if v == file_rel_to_src:
                        old_file_rel = k
                        break
                if not old_file_rel:
                    old_file_rel = file_rel_to_src # Not moved (like App.tsx)
                
                old_file_dir = Path(old_file_rel).parent
                # calculate old resolved path
                old_resolved = (old_file_dir / import_path).resolve()
                try:
                    old_resolved_rel = str(old_resolved.relative_to(src_dir.resolve()))
                except ValueError:
                    return match.group(0) # Out of src, leave it
                
                # Find if the target moved
                # The target might have an extension or index.ts
                possible_targets = [
                    old_resolved_rel + ".tsx",
                    old_resolved_rel + ".ts",
                    old_resolved_rel + "/index.ts",
                    old_resolved_rel + "/index.tsx",
                    old_resolved_rel,
                ]
                
                new_target_rel = None
                for pt in possible_targets:
                    if pt in file_moves:
                        new_target_rel = file_moves[pt]
                        break
                
                if not new_target_rel:
                    # Maybe it didn't move
                    new_target_rel = old_resolved_rel
                
                # Now compute new relative path from NEW file location to NEW target location
                # Remove extension from new_target_rel
                if new_target_rel.endswith('.tsx'):
                    new_target_rel = new_target_rel[:-4]
                elif new_target_rel.endswith('.ts'):
                    new_target_rel = new_target_rel[:-3]
                elif new_target_rel.endswith('.css'):
                    pass # keep .css
                    
                new_rel = get_new_relative_path(file_rel_to_src, new_target_rel)
                return prefix + new_rel + suffix
            return match.group(0)

        new_content = import_pattern.sub(replace_import, new_content)
        
        if new_content != content:
            file_path.write_text(new_content)

if __name__ == "__main__":
    main()
