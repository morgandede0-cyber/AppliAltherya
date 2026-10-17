"""Consistent, verified snapshots; never copy a live SQLite file or its WAL."""
import os, sqlite3, time, asyncio, logging
from pathlib import Path
from contextlib import closing
log = logging.getLogger('altherya.saves')

def backup(database, force=False):
    database = Path(database).resolve()
    if not database.is_file(): return None
    folder = Path(os.getenv('ACTIVITY_BACKUP_DIR', str(database.parent/'backups'))).resolve()
    folder.mkdir(parents=True, exist_ok=True)
    prefix = database.name + '.'
    previous = sorted(folder.glob(prefix+'*.sqlite3'), key=lambda p:p.stat().st_mtime)
    with closing(sqlite3.connect(database)) as source:
        if source.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise RuntimeError('Sauvegarde du jeu incohérente : arrêt pour préserver les données. Restaurer une copie vérifiée.')
        if not force and previous and time.time()-previous[-1].stat().st_mtime < 6*3600: return previous[-1]
        target = folder/(prefix+str(time.time_ns())+'.sqlite3')
        temporary = target.with_suffix('.tmp')
        try:
            with closing(sqlite3.connect(temporary)) as dest:
                source.backup(dest)
                if dest.execute('PRAGMA quick_check').fetchone()[0] != 'ok': raise RuntimeError('Copie de sauvegarde invalide')
            with temporary.open('rb') as f: os.fsync(f.fileno())
            temporary.replace(target)
            # Keep the latest 28 copies (up to seven days at a six-hour cadence).
            for old in previous[:-27]: old.unlink()
            return target
        finally:
            temporary.unlink(missing_ok=True)

async def save_lifecycle(app):
    service = app['discord_service_factory']()
    async def loop():
        while True:
            await asyncio.sleep(6*3600)
            try: await asyncio.to_thread(backup, service.path)
            except Exception: log.exception('Échec de la copie de sauvegarde périodique')
    task = asyncio.create_task(loop())
    yield
    task.cancel()
    try: await task
    except asyncio.CancelledError: pass
    await asyncio.to_thread(backup, service.path, True)

if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description='Créer et vérifier une copie complète de la sauvegarde Altherya.')
    parser.add_argument('database',type=Path)
    args=parser.parse_args()
    print(backup(args.database,force=True))
