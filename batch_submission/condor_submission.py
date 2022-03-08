from batch_submission.batch_submission import AbstractBatchSubmission, do_multiple_subprocess_attempts
import os
import htcondor

schedd = htcondor.Schedd()

def get_jobid_from_submission(submission):
    """
    Parameters
    ----------
        The byte-string returned by submitting a job to the slurm system

    Returns
    -------
        int
            The jobid of the submission.
    """
    raise ValuError("Not yet implemented")
    return job_id


def parse_queue_output(jobqueue):
    """
    Parameters
    ----------
        list of ClassAd
            the list of ClassAds returned by htcondor.Schedd().query().

    Returns
    -------
        set of int
            The jobids of the currenty submitted and running jobs on the slurm batch system.
    """
    job_ids = set()
    for el in jobqueue:
        job_status = el["JobStatus"]
        running = (job_status == htcondor.JobStatus.RUNNING) or (job_status == htcondor.JobStatus.IDLE)
        if running:
            job_ids.add(el["ClusterId"])

    return job_ids

class CondorSubmission(AbstractBatchSubmission):
    def get_job_queue(self):
        """
        Get the queue of jobs currently running to the batch system by the user

        Parameters
        ----------

        Returns
        -------
            set of {int}
                A set of jobids for all jobs currently running
        """
        long_info = schedd.query(constraint="OWNER == \"{}\"".format(os.getenv("USER")), projection=["ClusterId", "JobStatus"])
        job_ids =  parse_queue_output(long_info)
        return job_ids

    def _submit(self):
        """
        Submit the job to the batch system, and return the jobid for book keeping.

        Parameters
        ----------

        Returns
        -------
            int
                The jobid of the submission.
        """
        submission = htcondor.Submit({\
            "Executable": self.script,\
            "request_memory": self.memory,\
            "request_cpus": 1,\
            "Error": self.error,\
            "Output": self.output,\
            "Log": self.output.replace(".out", ".log"),\
            "should_transfer_files": False,\
            "+JobFlavour": self.time,
        })
        submit_result = schedd.submit(submission)
        return submit_result.cluster()


AbstractBatchSubmission.register(CondorSubmission)
