library(eba)

args <- commandArgs(trailingOnly = TRUE)

for (fname in args) {
    print(paste('Processing', fname))
    M <- read.table(fname)

    ptime <- proc.time()

    p_fname = paste0(dirname(fname), '/', gsub('m-', 'p_old-', basename(fname)))
    if (file.exists(p_fname)) {
        print(paste('Reading', p_fname))
        p <- read.table(p_fname)
        res <- OptiPt(M, s=t(p))
    } else {
        res <- OptiPt(M)
    }
    print(proc.time() - ptime)

    out_fname = paste0(dirname(fname), '/', gsub('m-', 'p_new-', basename(fname)))
    write(t(res$coefficients), ncolumns=length(res$coefficients), file=out_fname)
    print(paste('Wrote', out_fname))
}
