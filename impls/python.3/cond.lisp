;; Trying to gronk lisp
;; 
					
(defmacro! cond (fn* (& xs) 
		     (if (> (count xs) 0) 
			 (list 
			  (quote if) (first xs) 
			  (if (> (count xs) 1) 
			      (nth xs 1)
 
			      (throw "odd number of forms to cond")
			      ) 
						
			  (cons (quote cond) (rest (rest xs)))
			  )
			 )
		     )
  )

(println (macroexpand (cond x y a b c d)))


(def! reduce
    (fn* (f init xs)
	 (if (empty? xs) 
	     init 

	     (reduce f (f init (first xs)) (rest xs))
  	     )

	 )
  )

(def! sum (fn* [xs]
	       (reduce + 0 xs)
	       ))

(println (sum []))
(println (sum [1 2 3]))

(def! max (fn* [xs] (reduce (fn* [acc x] (if (< acc x) x acc)) 0 xs)))

(println (max [1 2 3]))

(println (reduce str "" ["Woody" "Potato" "Buzz"]))

(def! rcons (fn* [list e] (cons e list)))

(println (reduce rcons [] [1 2 3 4 5 6]))

(println (reduce (fn* [list e] (cons e list)) [] [1 2 3 4 5 6]))
