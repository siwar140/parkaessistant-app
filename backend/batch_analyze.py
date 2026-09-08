# batch_analyze.py
# Script pour analyser tous les fichiers audio d'un dossier en lot

import os
import sys
import json
import time
from pathlib import Path
from app.ml_inference import predict
import warnings
warnings.filterwarnings('ignore')


def batch_analyze(folder_path, output_file="results.json"):
    """
    Analyse tous les fichiers audio d'un dossier.
    
    Args:
        folder_path: Chemin du dossier contenant les fichiers audio
        output_file: Fichier JSON pour sauvegarder les résultats
    """
    # Extensions audio supportées
    audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac'}
    
    # Récupérer tous les fichiers audio
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Le dossier n'existe pas: {folder_path}")
        return
    
    audio_files = [f for f in folder.iterdir() if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print(f"❌ Aucun fichier audio trouvé dans {folder_path}")
        print(f"   Extensions supportées: {', '.join(audio_extensions)}")
        return
    
    print("=" * 70)
    print(f"📂 DOSSIER: {folder_path}")
    print(f"🎵 FICHIERS: {len(audio_files)} fichiers audio trouvés")
    print("=" * 70)
    
    results = []
    success_count = 0
    error_count = 0
    sain_count = 0
    malade_count = 0
    
    for i, file_path in enumerate(audio_files, 1):
        print(f"\n[{i}/{len(audio_files)}] Analyse de: {file_path.name}")
        print("-" * 50)
        
        try:
            start_time = time.time()
            result = predict(str(file_path))
            elapsed = time.time() - start_time
            
            # Compter les résultats
            if result["result"] == "Sain":
                sain_count += 1
                status = "✅"
            else:
                malade_count += 1
                status = "⚠️"
            
            # Afficher le résultat
            print(f"{status} Résultat: {result['result']}")
            print(f"   Confiance: {result['confidence']*100:.1f}%")
            print(f"   Probabilité: {result['probability']*100:.2f}%")
            print(f"   ⏱️  Temps: {elapsed:.2f}s")
            
            # Sauvegarder le résultat
            results.append({
                "file": file_path.name,
                "path": str(file_path),
                "result": result["result"],
                "confidence": round(result["confidence"], 4),
                "probability": round(result["probability"], 4),
                "time": round(elapsed, 2)
            })
            success_count += 1
            
        except Exception as e:
            print(f"❌ Erreur: {str(e)}")
            results.append({
                "file": file_path.name,
                "path": str(file_path),
                "error": str(e)
            })
            error_count += 1
    
    # Afficher les statistiques
    print("\n" + "=" * 70)
    print("📊 STATISTIQUES")
    print("=" * 70)
    print(f"   Total fichiers: {len(audio_files)}")
    print(f"   ✅ Succès: {success_count}")
    print(f"   ❌ Erreurs: {error_count}")
    
    if success_count > 0:
        print(f"   🟢 Sain: {sain_count} ({sain_count/success_count*100:.1f}%)")
        print(f"   🔴 Malade: {malade_count} ({malade_count/success_count*100:.1f}%)")
    
    # Sauvegarder les résultats en JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Résultats sauvegardés dans: {output_file}")
    print("=" * 70)


def batch_analyze_csv(folder_path, output_file="results.csv"):
    """Analyse tous les fichiers audio et exporte en CSV."""
    
    import csv
    
    audio_extensions = {'.wav', '.mp3', '.ogg', '.flac', '.m4a', '.aac'}
    folder = Path(folder_path)
    
    if not folder.exists():
        print(f"❌ Le dossier n'existe pas: {folder_path}")
        return
    
    audio_files = [f for f in folder.iterdir() if f.suffix.lower() in audio_extensions]
    
    if not audio_files:
        print(f"❌ Aucun fichier audio trouvé")
        return
    
    print(f"📂 Dossier: {folder_path}")
    print(f"🎵 {len(audio_files)} fichiers trouvés\n")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Fichier', 'Résultat', 'Confiance (%)', 'Probabilité (%)', 'Temps (s)'])
        
        for i, file_path in enumerate(audio_files, 1):
            try:
                start = time.time()
                result = predict(str(file_path))
                elapsed = time.time() - start
                
                writer.writerow([
                    file_path.name,
                    result["result"],
                    f"{result['confidence']*100:.1f}",
                    f"{result['probability']*100:.2f}",
                    f"{elapsed:.2f}"
                ])
                
                status = "✅" if result["result"] == "Sain" else "⚠️"
                print(f"[{i}/{len(audio_files)}] {status} {file_path.name} → {result['result']} ({result['confidence']*100:.1f}%)")
                
            except Exception as e:
                writer.writerow([file_path.name, "ERREUR", "", "", str(e)])
                print(f"[{i}/{len(audio_files)}] ❌ {file_path.name} → Erreur: {e}")
    
    print(f"\n💾 Résultats sauvegardés dans: {output_file}")


if __name__ == "__main__":
    # Utilisation:
    # python batch_analyze.py "C:/chemin/vers/dossier"
    # python batch_analyze.py "C:/chemin/vers/dossier" --csv
    
    if len(sys.argv) < 2:
        print("=" * 70)
        print("📂 BATCH ANALYZE - Analyse audio en lot")
        print("=" * 70)
        print("\n📌 Utilisation:")
        print("   python batch_analyze.py <dossier>")
        print("   python batch_analyze.py <dossier> --csv")
        print("\n📌 Exemples:")
        print('   python batch_analyze.py "C:/Users/MSI/Desktop/pd_project/DATA/Original/Control"')
        print('   python batch_analyze.py "C:/Users/MSI/Desktop/mes_audios" --csv')
        print("\n📌 Fichiers de sortie:")
        print("   results.json  - Résultats détaillés (format JSON)")
        print("   results.csv   - Résultats (format CSV avec --csv)")
        print("=" * 70)
        sys.exit(1)
    
    folder_path = sys.argv[1]
    use_csv = "--csv" in sys.argv
    
    if use_csv:
        batch_analyze_csv(folder_path)
    else:
        batch_analyze(folder_path)