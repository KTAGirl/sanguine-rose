import sanguine.tasks as tasks
from sanguine.cache.available_files import FileRetriever, AvailableFiles, GithubFolder
from sanguine.cache.folder_cache import FileOnDisk, FolderCache
from sanguine.common import *
from sanguine.project_config import ProjectConfig


class WholeCache:
    # WholeCache, once ready_task_name() is reached, contains whole information about the folders, and available files
    #             all the information is in-memory, so it can work incredibly fast
    vfscache: FolderCache
    available: AvailableFiles
    _SYNCOWNTASKNAME: str = 'sanguine.wholecache.sync'

    def __init__(self, by: str, projectcfg: ProjectConfig, githubfolders: list[GithubFolder]) -> None:
        self.available = AvailableFiles(by, projectcfg.cache_dir, projectcfg.tmp_dir, projectcfg.github_dir,
                                        projectcfg.download_dirs, githubfolders)

        folderstocache: FolderListToCache = projectcfg.active_vfs_folders()
        self.vfscache = FolderCache(projectcfg.cache_dir, 'vfs', folderstocache)

    def start_tasks(self, parallel: tasks.Parallel) -> None:
        self.vfscache.start_tasks(parallel)
        self.available.start_tasks(parallel)

        syncowntask = tasks.OwnTask(WholeCache._SYNCOWNTASKNAME,
                                    lambda _, _1, _2: self._start_sync_own_task_func(), None,
                                    [self.vfscache.ready_task_name(),
                                     self.available.ready_task_name()])
        parallel.add_task(syncowntask)

    def _start_sync_own_task_func(self) -> None:
        pass  # do nothing, this task is necessary only to synchronize

    @staticmethod
    def ready_task_name() -> str:
        return WholeCache._SYNCOWNTASKNAME

    def all_vfs_files(self) -> Iterable[FileOnDisk]:
        return self.vfscache.all_files()

    def file_retrievers_by_hash(self, h: bytes) -> list[FileRetriever]:  # resolved as fully as feasible
        return self.available.file_retrievers_by_hash(h)

    '''
    def file_retrievers_by_name(self, fname: str) -> list[FileRetriever]:  # resolved as fully as feasible
        return self.available.file_retrievers_by_name(fname)
    '''
