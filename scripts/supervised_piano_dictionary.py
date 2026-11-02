"""Nonnegative timbre adaptation using fitting-only MIDI pitch masks."""
import numpy as np


def learn_dictionary(prior,observed,mask,epochs=40,updates=4,ridge=1.):
    prior=np.asarray(prior,dtype=float)
    observed=np.asarray(observed,dtype=float)
    mask=np.asarray(mask)
    if (prior.ndim!=2 or observed.ndim!=2 or prior.shape[0]!=observed.shape[0] or
        mask.shape!=(prior.shape[1],observed.shape[1]) or mask.dtype.kind!='b' or
        not np.isfinite(prior).all() or not np.isfinite(observed).all() or
        (prior<0).any() or (observed<0).any() or
        not np.allclose(np.linalg.norm(prior,axis=0),1.,atol=1e-8) or
        epochs<1 or updates<1 or not np.isfinite(ridge) or ridge<=0):
        raise ValueError('Need normalized nonnegative bases, finite observations and a matching boolean fitting mask')
    active=mask.any(axis=1)
    if not active.any():
        return prior.copy()
    matrix=prior.copy()
    matrix[:,active]=np.maximum(matrix[:,active],1e-8)
    matrix[:,active]/=np.linalg.norm(matrix[:,active],axis=0)
    activation=np.maximum(matrix.T@observed,1e-12)*mask
    for _ in range(epochs):
        projection=matrix.T@observed
        gram=matrix.T@matrix
        for _ in range(updates):
            activation*=projection/np.maximum(gram@activation,1e-12)
        numerator=observed@activation.T+ridge*prior
        denominator=matrix@(activation@activation.T)+ridge*matrix
        matrix*=numerator/np.maximum(denominator,1e-12)
        norms=np.maximum(np.linalg.norm(matrix,axis=0),1e-12)
        matrix/=norms
        activation*=norms[:,None]
        # No co-occurrence evidence can alter a never-observed pitch.
        matrix[:,~active]=prior[:,~active]
    assert np.isfinite(matrix).all() and (matrix>=0).all()
    return matrix
