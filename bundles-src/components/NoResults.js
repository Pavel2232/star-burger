import React, {Component} from 'react';

const NoResults = () =>{
    return(
        <div className="row">
            <div className="col-sm-3 col-md-3 col-lg-3"></div>
            <div className="col-sm-6 col-md-6 col-lg-6">
                <center>
                <h2>Sorry, no products matched your search!</h2>
                <p>Enter a different keyword and try.</p>
                </center>
            </div>
            <div className="col-sm-3 col-md-3 col-lg-3"></div>
        </div>
    )
};

export default NoResults;
